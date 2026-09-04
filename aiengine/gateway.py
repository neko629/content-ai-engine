"""LLM 统一网关（参考实现）。

把「多供应商 × 多模型」收敛到一个入口，业务只按**用途**调用：
    gateway.call(purpose="title", messages=[...])

候选选择与降级逻辑（镜像生产实现）：
1. 指定 model_name → 只命中该模型；
2. 按用途配置的有序候选逐个尝试；
3. 单个候选调用失败 → 自动 fallback 到下一个，状态标记 ``fallback``；
4. 全部失败抛 ``LLMAllFailed``（上层按用途决定重试或 fail-open）。

Mock provider：不配置任何 key 也能跑通全链路；接真实模型只需注入
``LLM_BASE_URL`` / ``LLM_API_KEY`` 两个环境变量（任意 OpenAI 兼容端点）。
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

from .config import EngineConfig, ModelConfig
from .usage import UsageCounter


class LLMError(RuntimeError):
    """用途对应的所有候选模型都失败。"""


@dataclass
class Completion:
    content: str
    provider: str
    model: str
    status: str          # ok | fallback
    attempts: int
    duration_ms: int
    prompt_tokens: int
    completion_tokens: int


class _BaseProvider:
    """返回 (content_text, usage_dict)。失败请直接抛异常，交给网关降级。"""

    def complete(
        self,
        cfg: ModelConfig,
        messages: list[dict],
        temperature: float,
        json_mode: bool,
        purpose: str,
    ) -> tuple[str, dict]:
        raise NotImplementedError


class OpenAICompatibleProvider(_BaseProvider):
    """任意 OpenAI 兼容 Chat Completions 端点（urllib 实现，无第三方依赖）。"""

    def complete(self, cfg, messages, temperature, json_mode, purpose=None):
        base_url = (cfg.base_url() or "").rstrip("/")
        api_key = cfg.api_key()
        if not base_url or not api_key:
            raise LLMError(f"model[{cfg.name}] 未配置 LLM_BASE_URL/LLM_API_KEY")
        if json_mode:
            messages = messages + [
                {"role": "system", "content": "You must respond with valid JSON only."}
            ]
        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        timeout = float(os.environ.get("LLM_TIMEOUT", "30"))
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (demo)
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {}) or {}
        return content, {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }


def _approx_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


class MockProvider(_BaseProvider):
    """离线 mock：让 demo 不依赖任何外部服务也能跑通，并演示降级路径。

    各用途返回「预置的、刻意带噪点」的输出，用于展示下游如何消化：
    - moderation 返回合法 JSON；
    - title / sd_prompt 返回合法 JSON；
    - storyboard 返回一段带着 ```json 围栏、单引号、尾逗号、True/None 的脏文本，
      用来演示 json_repair 的容错解析。
    """

    _STORYBOARD_DIRTY = """
好的，这是你的分镜脚本：

```json
{"title": '雨夜对决', "final": True, "pages": [
  {"page": 1, "panels": [
     {"scene": '两人在楼顶对峙，雨势渐大', "dialogue": '你终于来了。', "mood": '紧张'},
     {"scene": '镜头拉远，城市灯火如海', "dialogue": '', "mood": '孤独',},
  ]},
  {"page": 2, "panels": [
     {"scene": '雨幕中拔出刀', "dialogue": '这一次，我不会再逃。', "mood": '决绝',},
  ]},
]}
```
以上是逐页逐格的可执行结构。
"""

    def complete(self, cfg, messages, temperature, json_mode, purpose="default"):
        user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user = msg.get("content", "")
                break
        content, pt, ct = self._fabricate(purpose, user.strip())
        return content, {
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": pt + ct,
        }

    def _fabricate(self, purpose: str, tail: str):
        if purpose == "moderation":
            out = json.dumps({"ad": False, "contact": False, "gore": False}, ensure_ascii=False)
            return out, _approx_tokens(tail), _approx_tokens(out)

        if purpose == "title":
            t = tail
            if "原标题：" in t:
                t = t.split("原标题：", 1)[1]
            clean = t.strip()[:40]
            style = "｜4K 高清完整版" if (hashlib.md5(clean.encode()).digest()[0] % 2) else "｜一口气看完"
            out = json.dumps({"title": f"{clean}{style}"}, ensure_ascii=False)
            return out, _approx_tokens(clean), _approx_tokens(out)

        if purpose == "sd_prompt":
            seed = tail.strip().replace("封面：", "")[:24]
            out = json.dumps(
                {
                    "prompt": (
                        "masterpiece, cinematic lighting, ultra detailed, "
                        f"dynamic composition, subject: {seed}"
                    ),
                    "negative_prompt": "lowres, blur, watermark, text",
                },
                ensure_ascii=False,
            )
            return out, _approx_tokens(seed), _approx_tokens(out)

        if purpose == "storyboard":
            return self._STORYBOARD_DIRTY, 24, _approx_tokens(self._STORYBOARD_DIRTY)

        echo = f"mock echo: {tail[:80]}"
        return echo, _approx_tokens(tail), len(echo)


class LLMGateway:
    """线程安全、带用量审计的 LLM 调用入口。"""

    def __init__(self, cfg: EngineConfig, usage: UsageCounter) -> None:
        self._cfg = cfg
        self._usage = usage
        self._by_name = {m.name: m for m in cfg.models}
        self._random = random.Random()

    # ---- 候选挑选（与生产 *_select_llm_configs 同思路） ----
    def _candidates(self, purpose: Optional[str], model_name: Optional[str]) -> list[ModelConfig]:
        if model_name:
            cfg = self._by_name.get(model_name)
            if cfg is None:
                raise LLMError(f"未知模型: {model_name}")
            return [cfg]

        chosen: list[ModelConfig] = []
        if purpose and purpose in self._cfg.purposes:
            names = self._cfg.purposes[purpose]
            chosen = [self._by_name[n] for n in names if n in self._by_name]
        if not chosen:
            # 用途未配置 → 退化为「负载均衡组 + 兜底」
            lb = [m for m in self._cfg.models if m.load_balance]
            self._random.shuffle(lb)
            chosen = lb
            chosen += [m for m in self._cfg.models if m.is_default and m not in chosen]
        if not chosen:
            raise LLMError(f"purpose[{purpose}] 没有任何可用模型")
        return chosen

    # ---- 供应商实例 ----
    def _provider_for(self, cfg: ModelConfig) -> _BaseProvider:
        if cfg.provider == "openai_compatible":
            return OpenAICompatibleProvider()
        if cfg.provider == "mock":
            return MockProvider()
        raise LLMError(f"未知 provider: {cfg.provider}")

    def call(
        self,
        purpose: str,
        messages: list[dict],
        *,
        temperature: float = 0.7,
        json_mode: bool = False,
        model_name: Optional[str] = None,
    ) -> Completion:
        start = time.time()
        last_err = ""
        for idx, cfg in enumerate(self._candidates(purpose, model_name)):
            try:
                provider = self._provider_for(cfg)
                content, usage = provider.complete(cfg, messages, temperature, json_mode, purpose)
            except Exception as exc:  # noqa: BLE001 —— 供应商级失败交给降级，不在这一层中断
                last_err = f"{cfg.name}: {exc}"
                self._usage.record_call(
                    purpose, cfg.provider, cfg.model, "error",
                    attempts=idx + 1, duration_ms=int((time.time() - start) * 1000),
                    error=str(exc)[:200],
                )
                continue
            status = "ok" if idx == 0 else "fallback"
            self._usage.add_tokens(purpose, cfg.provider, usage.get("total_tokens", 0))
            self._usage.record_call(
                purpose, cfg.provider, cfg.model, status,
                attempts=idx + 1, duration_ms=int((time.time() - start) * 1000),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            )
            return Completion(
                content=content,
                provider=cfg.provider,
                model=cfg.model,
                status=status,
                attempts=idx + 1,
                duration_ms=int((time.time() - start) * 1000),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            )
        raise LLMError(f"purpose[{purpose}] 全部 {len(self._candidates(purpose, model_name))} 个候选失败：{last_err}")
