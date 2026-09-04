"""AI 标题改写（参考实现）。

LLM 输出质量工程的关键模式都在这里：
1. 明确要求 JSON 输出，改写后还要过一层**强清洗** ``_normalize`` —— 剥掉模型自报家门的
   污染（"标题："、包裹引号、多余空白）和可能的越界符号；
2. **拒答/元回复检测** ``_is_meta_response`` —— 模型可能不听话地输出"我无法改写"而不是结果；
3. 检测到污染或拒答时，**降温度重试一次**（0.7 → 0.3），让输出更收敛；
4. 仍然失败时回退原标题，绝不让一次模型抽风把内容改坏。
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from .gateway import LLMGateway
from .json_repair import extract_json

_MAX_LEN = 60
_META_MARKERS = (
    "抱歉", "无法", "拒绝", "不能", "不好意思",
    "i can't", "i cannot", "sorry", "as an ai",
)


def normalize_title(raw: str) -> str:
    """强清洗：剥污染标签/包裹引号/多余空白，并截断超长标题。"""
    t = (raw or "").strip()
    # 剥掉模型常见"自报家门"式前缀
    t = re.sub(r"^(标题|重写|改写|优化|润色|好的|没问题)[：:\s]*", "", t)
    # 剥整串包裹的引号/书名号
    t = re.sub(r"^['\"「『【【“](.*?)['\"」』】】”]$", r"\1", t)
    # 若是"我已经改好了："式的残留，保留冒号后内容
    t = re.sub(r"^(好的，|已为你|帮你)*改写(结果)?[：:\s]*", "", t)
    t = " ".join(t.split())
    return t[:_MAX_LEN]


def is_meta_response(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _META_MARKERS) or not text


@dataclass
class TitleResult:
    ok: bool
    title: str
    changed: bool = False
    attempts: int = 0
    meta: dict = field(default_factory=dict)


class TitleRewriter:
    _SYSTEM = (
        "你是标题优化引擎。把原标题改写成更吸引点击但仍属实的标题，"
        '保持与内容一致。只输出 JSON：{"title": "改写后的标题"}'
    )

    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    def rewrite(self, title: str) -> TitleResult:
        source = (title or "").strip()
        if not source:
            return TitleResult(ok=False, title="", reason="empty title")

        raw, comp = self._call(source, temperature=0.7)
        cleaned = normalize_title(raw)
        if is_meta_response(cleaned):
            # 降温度重试：让模型输出更收敛、更"听话"
            raw2, comp2 = self._call(source, temperature=0.3)
            cleaned = normalize_title(raw2)
            comp = comp2

        if is_meta_response(cleaned):
            return TitleResult(
                ok=False, title=source,
                meta={"error": "meta response after retry", "attempts": comp.attempts},
            )
        return TitleResult(
            ok=True,
            title=cleaned,
            changed=(cleaned != source),
            attempts=comp.attempts,
            meta={
                "provider": comp.provider, "model": comp.model,
                "status": comp.status, "duration_ms": comp.duration_ms, "ts": time.time(),
            },
        )

    def _call(self, title: str, *, temperature: float):
        messages = [
            {"role": "system", "content": self._SYSTEM},
            {"role": "user", "content": f"原标题：{title}"},
        ]
        comp = self._gateway.call("title", messages, temperature=temperature, json_mode=True)
        data, _ = extract_json(comp.content)
        raw = data.get("title", "") if isinstance(data, dict) else ""
        return raw, comp
