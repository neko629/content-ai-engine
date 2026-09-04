"""离线冒烟测试（零第三方依赖）：python3 tests/smoke.py"""
from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiengine.pipeline import PipelineEngine  # noqa: E402


def main() -> None:
    eng = PipelineEngine()

    # 1) 单条：审核+标题+封面
    r = eng.process("雨夜逆袭：少年觉醒异能", text="一段用于审核的正文。")
    assert r["status"] in ("ok", "blocked"), r
    assert r["title"]
    assert r["moderation"]["passed"] in (True, False)   # mock 默认全 False
    assert r["cover_data_uri"] and r["cover_data_uri"].startswith("data:image/png")
    assert r["cover_status"] == "ok"
    steps = {s["name"] for s in r["steps"]}
    assert "moderation · LLM 文本审核" in steps
    assert "title · AI 标题改写" in steps
    assert "cover · SD 提示词 + 文生图" in steps

    # 2) 批量：空标题 → skipped，单条失败不拖垮整批
    b = eng.batch(["标题A", "", "标题C"])
    assert b["by_status"]["skipped"] == 1
    assert len(b["results"]) == 3

    # 3) 结构化输出：脏 JSON 能修出来
    st = eng.storyboard("雨夜对决")
    assert st["repair_meta"]["repaired"] is True
    assert st["data"]["pages"][0]["page"] == 1

    # 4) SD 提示词缓存生效（二次调用 cached=True）
    first = eng.covers.generate_sd_prompt("封面：测试标题")
    second = eng.covers.generate_sd_prompt("封面：测试标题")
    assert first["cached"] is False and second["cached"] is True

    print("SMOKE PASS")
    print(json.dumps({
        "single_status": r["status"],
        "batch_by_status": b["by_status"],
        "storyboard_pages": len(st["data"]["pages"]),
        "sd_cache_second_call": second["cached"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
