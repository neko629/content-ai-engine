"""文本内容安全审核（参考实现）。

三层治理中的第一层：入库前的 LLM 文本审核。
- 让模型按「固定类别 + 固定 JSON 结构」输出，结果可编程消费；
- **fail-open**：审核服务不可用时默认放行并标记 degraded，不让审核故障阻塞主业务
  （可用性优先的取舍，可在 config 里关闭）。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .gateway import LLMGateway, LLMError
from .json_repair import extract_json

CATEGORIES = ("ad", "contact", "gore")   # 广告 / 联系方式 / 血腥(示例类目)


@dataclass
class ModerationResult:
    passed: bool
    flags: dict[str, bool] = field(default_factory=dict)
    degraded: bool = False                 # True = 走了 fail-open
    meta: dict = field(default_factory=dict)


class TextModerator:
    _SYSTEM = (
        "你是内容安全审核引擎。判断文本是否命中以下违规类别："
        f"{'、'.join(CATEGORIES)}。只输出 JSON，形如："
        + '{"ad": bool, "contact": bool, "gore": bool}'
    )

    def __init__(self, gateway: LLMGateway, *, fail_open: bool = True) -> None:
        self._gateway = gateway
        self._fail_open = fail_open

    def moderate(self, text: str) -> ModerationResult:
        text = (text or "").strip()
        if not text:
            return ModerationResult(passed=True, flags={})
        messages = [
            {"role": "system", "content": self._SYSTEM},
            {"role": "user", "content": text[:2000]},
        ]
        try:
            comp = self._gateway.call("moderation", messages, temperature=0.0, json_mode=True)
        except LLMError as exc:
            if self._fail_open:
                return ModerationResult(
                    passed=True, flags={}, degraded=True,
                    meta={"error": str(exc), "ts": time.time()},
                )
            raise

        flags = self._parse(comp.content)
        return ModerationResult(
            passed=not any(flags.values()),
            flags=flags,
            meta={
                "provider": comp.provider,
                "model": comp.model,
                "status": comp.status,
                "attempts": comp.attempts,
                "duration_ms": comp.duration_ms,
            },
        )

    @staticmethod
    def _parse(content: str) -> dict[str, bool]:
        data, _ = extract_json(content)
        if not isinstance(data, dict):
            return {}
        return {c: bool(data.get(c, False)) for c in CATEGORIES}
