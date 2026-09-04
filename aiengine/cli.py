"""命令行入口。

用法：
  python3 -m aiengine.cli run "标题" [--text 正文]   # 跑一条加工链
  python3 -m aiengine.cli batch                     # 跑内置批量示例
  python3 -m aiengine.cli storyboard "主题"          # 演示脏 JSON 容错解析
  python3 -m aiengine.cli serve [--port 8010]       # 起 web demo
  python3 -m aiengine.cli usage                     # 用量/审计快照
  python3 -m aiengine.cli selftest                  # 离线自检
"""
from __future__ import annotations

import argparse
import json

from .pipeline import PipelineEngine

_SAMPLE = [
    "雨夜逆袭：少年觉醒异能",
    "公司里最后一位实习生",
    "开局获得无字天书",
    "山那边的旧祠堂",
]


def _print(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="aiengine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="跑一条 AI 加工链")
    p.add_argument("title")
    p.add_argument("--text", default=None)

    sub.add_parser("batch", help="内置批量示例")
    sub.add_parser("storyboard", help="演示脏 JSON → 容错解析").add_argument("theme", nargs="?", default="雨夜对决")
    sub.add_parser("usage", help="用量/调用审计")
    sub.add_parser("selftest", help="离线自检")
    s = sub.add_parser("serve", help="起 web demo")
    s.add_argument("--port", type=int, default=None)

    args = parser.parse_args()
    eng = PipelineEngine()

    if args.cmd == "run":
        _print(eng.process(args.title, args.text))
    elif args.cmd == "batch":
        _print(eng.batch(_SAMPLE))
    elif args.cmd == "storyboard":
        _print(eng.storyboard(args.theme))
    elif args.cmd == "usage":
        _print({"usage": eng.usage.snapshot(), "recent_calls": eng.usage.recent_calls(10)})
    elif args.cmd == "selftest":
        selftest(eng)
    elif args.cmd == "serve":
        from .webserver import serve
        serve(eng, port=args.port)


def selftest(eng: PipelineEngine) -> None:
    print("== 单条加工链 ==")
    r = eng.process(_SAMPLE[0])
    assert r["status"] in ("ok", "blocked"), r
    assert r["title"], "标题不应为空"
    assert r["cover_status"] == "ok", "封面应已生成"
    assert any(s["degraded"] is False or s["ok"] for s in r["steps"])
    print(f"  status={r['status']}  title={r['title']}  cover={r['cover_status']}  {r['duration_ms']}ms")

    print("== 批量（含空标题 → skipped）==")
    b = eng.batch([*_SAMPLE, ""])
    assert b["by_status"]["skipped"] >= 1
    print(f"  {b['by_status']}")

    print("== 脏 JSON 容错解析（storyboard）==")
    st = eng.storyboard("雨夜对决")
    assert st["repair_meta"]["repaired"] is True
    pages = st["data"]["pages"]
    assert len(pages) >= 1 and pages[0]["panels"][0]["scene"]
    print(f"  repaired={st['repair_meta']['repaired']} pages={len(pages)} "
          f"title={st['data']['title']}")

    print("== 用量快照 ==")
    print(" ", json.dumps(eng.usage.snapshot(), ensure_ascii=False))
    print("SELFTEST PASS")


if __name__ == "__main__":
    main()
