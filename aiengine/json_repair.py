"""大模型结构化输出工程：容错 JSON 解析 + 结构校验 + 带错误反馈重试。

LLM 输出不可靠是常态，参考实现分三层消化：
1. ``extract_json``      —— 四段容错：直接解析 → 去代码围栏 → 截取最外层花括号 → 自动修复；
2. 自动修复                —— 单引号 → 双引号、True/False/None → true/false/null、去尾逗号；
3. ``retry_with_feedback`` —— 解析失败或结构校验失败时，把「具体错误」回填进下一次生成
   （生产里这段就是让模型看自己错在哪、带反馈再生成一次）。
"""
from __future__ import annotations

import json
import re
from typing import Callable, Optional

# ---- 1. 容错解析 ----


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return t


def _outer_braces(text: str) -> str:
    """截取第一个 { 到最后一个 } 之间的内容。"""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def _auto_repair(text: str) -> str:
    t = text
    t = t.replace("'", '"')                                  # 单引号 → 双引号
    t = re.sub(r"(?<![\w\"'])(True|False|None)(?![\w\"'])",  # 布尔/空值大写 → JSON 字面量
               lambda m: m.group(1).lower(), t)
    t = re.sub(r",\s*([}\]])", r"\1", t)                     # 去尾逗号
    return t


def extract_json(raw: str) -> tuple[Optional[dict], str]:
    """返回 (data, '') 或 (None, 失败原因)。"""
    if not raw or not raw.strip():
        return None, "empty output"

    attempts = []
    original = raw.strip()
    fenced = _strip_code_fence(raw)
    # 依次尝试：原文 / 围栏剥离 / 截取最外层花括号（原文与剥离后各一次）→ 修复版
    for candidate in (original, fenced, _outer_braces(original), _outer_braces(fenced)):
        if candidate not in attempts:
            attempts.append(candidate)
    for candidate in list(attempts):
        repaired = _auto_repair(candidate)
        if repaired not in attempts:
            attempts.append(repaired)

    last_err = ""
    for candidate in attempts:
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data, ""
        except json.JSONDecodeError as exc:
            last_err = str(exc)
    return None, f"not valid JSON after {len(attempts)} attempts: {last_err}"


# ---- 2. 结构校验（业务自定义回调，返回错误串，空串 = 通过） ----
Validator = Callable[[dict], str]


def validate_storyboard(data: dict) -> str:
    if not isinstance(data, dict):
        return "must be an object"
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        return "missing non-empty `title`"
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        return "missing non-empty `pages` array"
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("page"), int):
            return "each page must have an int `page`"
        panels = page.get("panels")
        if not isinstance(panels, list) or not panels:
            return f"page {page.get('page')} has no `panels`"
        for panel in panels:
            if not isinstance(panel, dict) or not isinstance(panel.get("scene"), str):
                return f"page {page.get('page')} panel missing string `scene`"
    return ""


# ---- 3. 带错误反馈重试 ----
class JsonOutputError(RuntimeError):
    pass


def retry_with_feedback(
    generate: Callable[[str], str],
    validator: Validator,
    max_attempts: int = 2,
) -> tuple[dict, dict]:
    """generator(feedback) 产出一次 LLM 文本；失败原因作为 feedback 回填重试。

    返回 (data, meta)；全部失败抛 JsonOutputError。
    """
    feedback = ""
    for attempt in range(1, max_attempts + 1):
        raw = generate(feedback)
        data, err = extract_json(raw)
        repaired = data is not None
        if data is not None:
            verr = validator(data)
            if not verr:
                return data, {"attempts": attempt, "repaired": repaired}
            feedback = f"结构不合法：{verr}。请严格按 JSON 输出。"
        else:
            feedback = f"输出不是合法 JSON：{err}。请只输出 JSON。"
    raise JsonOutputError(feedback)
