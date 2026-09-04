"""零依赖 HTTP demo 服务（Python 标准库 http.server）。

接口：
  GET  /                 -> 交互页
  GET  /api/health       -> 健康检查
  GET  /api/usage        -> 用量/调用审计快照
  POST /api/pipeline     {title, text?}             -> 单条 AI 加工链
  POST /api/batch        {titles: [...], text_map?}  -> 批量加工（含 skipped/failed 语义）
  POST /api/storyboard   {theme}                    -> LLM 脏 JSON → 容错解析/校验/重试演示
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .pipeline import PipelineEngine

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _index_html() -> str:
    path = os.path.join(_ROOT, "web", "index.html")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class _Handler(BaseHTTPRequestHandler):
    engine: PipelineEngine
    index: str = ""

    def log_message(self, fmt, *args):  # 安静一点
        pass

    # ---- helpers ----
    def _json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            data = {}
        return data if isinstance(data, dict) else {}

    # ---- routes ----
    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            body = _index_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path in ("/api/health",):
            return self._json({"ok": True, "app": "content-ai-engine"})
        if self.path in ("/api/usage", "/api/snapshot"):
            eng: PipelineEngine = self.engine
            return self._json({"usage": eng.usage.snapshot(),
                               "recent_calls": eng.usage.recent_calls(15)})
        self.send_error(404)

    def do_POST(self):  # noqa: N802
        eng: PipelineEngine = self.engine
        body = self._read_body()
        if self.path == "/api/pipeline":
            return self._json(eng.process(body.get("title", ""), body.get("text")))
        if self.path == "/api/batch":
            titles = body.get("titles") or []
            return self._json(eng.batch([str(t) for t in titles],
                                        text_map=body.get("text_map")))
        if self.path == "/api/storyboard":
            return self._json(eng.storyboard(str(body.get("theme", "雨夜对决"))))
        self.send_error(404)


def serve(
    engine: PipelineEngine | None = None,
    host: str = "127.0.0.1",
    port: int | None = None,
) -> None:
    engine = engine or PipelineEngine()
    port = port or int(os.environ.get("PORT", "8010"))
    server = ThreadingHTTPServer((host, port), _Handler)
    _Handler.engine = engine
    print(f" * content-ai-engine demo  http://{host}:{port}")
    print(" * 未配置 LLM_BASE_URL/LLM_API_KEY → 走 Mock 模型离线演示；配置即切真实 OpenAI 兼容端点。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
