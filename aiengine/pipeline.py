"""内容 AI 加工链编排（参考实现）。

把三个 AI 环节串成一条**可追踪**的流水线，模拟真实"入库前加工"：
    文本审核 → 标题改写 → 封面生成（提示词 → 文生图 → 标记回写）

- 单条 ``process``：逐步记录 ok / degraded / duration，前端/CLI 都能看到每一步发生了什么；
- 批量 ``batch``：单条异常不拖垮整批（生产同款语义：ok / skipped / failed）；
- 审核拦截（blocked）模拟"不允许进入下一步发布"的业务闸门。
"""
from __future__ import annotations

import itertools
import time

from .config import EngineConfig, load
from .cover import CoverService
from .gateway import LLMGateway
from .json_repair import retry_with_feedback, validate_storyboard
from .moderation import TextModerator
from .title import TitleRewriter
from .usage import UsageCounter


class PipelineEngine:
    def __init__(self, cfg: EngineConfig | None = None) -> None:
        self.cfg = cfg or load()
        self.usage = UsageCounter()
        self.gateway = LLMGateway(self.cfg, self.usage)
        self.moderator = TextModerator(self.gateway, fail_open=self.cfg.fail_open_on_llm_error)
        self.titles = TitleRewriter(self.gateway)
        self.covers = CoverService(self.gateway)
        self._seq = itertools.count(1)

    # ---------------- 单条 ----------------
    def process(self, title: str, text: str | None = None) -> dict:
        start = time.time()
        item_id = next(self._seq)
        source = (title or "").strip()
        steps: list[dict] = []

        def step(name: str, ok: bool, detail: dict | None = None, degraded: bool = False) -> None:
            steps.append({
                "name": name, "ok": bool(ok),
                "degraded": bool(degraded), "detail": detail or {},
            })

        if not source:
            return {
                "item_id": item_id, "input_title": title, "status": "skipped",
                "reason": "empty title", "steps": steps,
                "duration_ms": int((time.time() - start) * 1000),
            }

        # 1) 文本审核（入库闸门）
        mod = self.moderator.moderate(text if text is not None else source)
        step(
            "moderation · LLM 文本审核", ok=mod.passed, degraded=mod.degraded,
            detail={"passed": mod.passed, "flags": mod.flags, "meta": mod.meta},
        )

        # 2) 标题改写
        tr = self.titles.rewrite(source)
        step(
            "title · AI 标题改写", ok=tr.ok,
            detail={"before": source, "after": tr.title,
                    "changed": getattr(tr, "changed", False), "meta": tr.meta},
        )
        final_title = tr.title if tr.ok else source

        # 3) 封面生成（提示词 → 文生图 → 完成钩子回写）
        cv = self.covers.submit_cover(item_id, final_title)
        ok_cover = cv.get("status") == "ok"
        step(
            "cover · SD 提示词 + 文生图", ok=ok_cover,
            detail={
                "status": cv.get("status"), "reason": cv.get("reason", ""),
                "task_id": cv.get("task_id"), "marker": cv.get("marker"),
                "sd_cached": cv.get("sd_cached"), "sd_prompt": cv.get("sd_prompt", "")[:80],
            },
        )

        # 4) 汇总（模拟"审核通过才允许上架/发布"的闸门）
        blocked = not mod.passed
        status = "ok"
        reason = ""
        if blocked:
            status, reason = "blocked", "moderation rejected"
        elif cv.get("status") == "failed":
            status, reason = "failed", cv.get("reason", "cover failed")
        elif cv.get("status") == "skipped":
            status, reason = "failed", cv.get("reason", "cover skipped")

        return {
            "item_id": item_id,
            "input_title": source,
            "status": status,
            "reason": reason,
            "title": final_title,
            "title_changed": bool(getattr(tr, "changed", False)),
            "moderation": {"passed": mod.passed, "flags": mod.flags, "degraded": mod.degraded},
            "cover_status": cv.get("status"),
            "cover_data_uri": cv.get("cover_data_uri"),
            "steps": steps,
            "duration_ms": int((time.time() - start) * 1000),
        }

    # ---------------- 批量 ----------------
    def batch(self, titles: list[str], *, text_map: dict[str, str] | None = None) -> dict:
        text_map = text_map or {}
        results = []
        for raw in titles:
            title = (raw or "").strip()
            if not title:
                results.append({"input": raw, "status": "skipped", "reason": "empty title"})
                continue
            try:
                r = self.process(title, text_map.get(title))
            except Exception as exc:  # noqa: BLE001 —— 单条失败不影响整批
                results.append({"input": raw, "status": "failed", "reason": str(exc)[:200]})
                continue
            results.append({
                "input": r["input_title"], "status": r["status"],
                "reason": r["reason"], "title": r["title"],
                "moderation": r["moderation"],
                "cover_status": r["cover_status"],
                "duration_ms": r["duration_ms"],
                "cover_data_uri": r.get("cover_data_uri"),
            })
        return {
            "total": len(results),
            "by_status": {s: sum(1 for x in results if x["status"] == s) for s in
                          ("ok", "blocked", "skipped", "failed")},
            "results": results,
        }

    # ---------------- 结构化输出演示 ----------------
    def storyboard(self, theme: str) -> dict:
        """漫画分镜：LLM 出脏 JSON → 容错解析/校验 → 必要时带错误反馈重试。"""

        def generate(feedback: str) -> str:
            user = f"主题：{theme}"
            if feedback:
                user += f"\n\n你上一次输出有问题：{feedback}\n请只输出 JSON。"
            msgs = [
                {"role": "system", "content": "你是漫画分镜编剧。输出 JSON："
                                              '{"title": str, "pages": [{"page": int, "panels": '
                                              '[{"scene": str, "dialogue": str, "mood": str}]}]}'},
                {"role": "user", "content": user},
            ]
            return self.gateway.call("storyboard", msgs, temperature=0.7).content

        data, meta = retry_with_feedback(generate, validate_storyboard)
        return {
            "theme": theme,
            "data": data,
            "repair_meta": meta,
            "explain": "LLM 常回带 ```json 围栏/单引号/尾逗号/True 的脏文本，"
                       "json_repair 负责容错解析；结构不合法则把错误回填再生成一次。",
        }
