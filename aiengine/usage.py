"""用量计量与调用审计。

生产版本的两点取舍在此保留概念：
- 计数走内存计数（生产为 Redis HINCRBY 热 key 计数），避免高并发直写数据库造成热行争用；
- 每隔一段时间由独立任务把计数原子回刷到持久层（此处暴露 ``snapshot``/``persist`` 语义）。
调用审计（谁、何时、哪个模型、多少 token、成败）独立追加，不影响主链路。
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Optional


class UsageCounter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens: dict[tuple[str, str], int] = {}      # (purpose, provider) -> tokens
        self._calls: list[dict] = []                       # 环形缓冲的调用日志
        self._MAX_CALLS = 500

    def record_call(
        self,
        purpose: str,
        provider: str,
        model: str,
        status: str,          # ok | fallback | error
        attempts: int,
        duration_ms: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        error: Optional[str] = None,
    ) -> None:
        with self._lock:
            self._calls.append(
                {
                    "ts": round(time.time(), 3),
                    "purpose": purpose,
                    "provider": provider,
                    "model": model,
                    "status": status,
                    "attempts": attempts,
                    "duration_ms": duration_ms,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "error": error,
                }
            )
            if len(self._calls) > self._MAX_CALLS:
                self._calls = self._calls[-self._MAX_CALLS:]

    def add_tokens(self, purpose: str, provider: str, total: int) -> None:
        with self._lock:
            key = (purpose, provider)
            self._tokens[key] = self._tokens.get(key, 0) + (total or 0)

    def snapshot(self) -> dict:
        with self._lock:
            per_purpose: dict[str, int] = {}
            per_provider: dict[str, int] = {}
            for (purpose, provider), tokens in self._tokens.items():
                per_purpose[purpose] = per_purpose.get(purpose, 0) + tokens
                per_provider[provider] = per_provider.get(provider, 0) + tokens
            return {
                "total_tokens": sum(self._tokens.values()),
                "per_purpose": per_purpose,
                "per_provider": per_provider,
                "calls_kept": len(self._calls),
            }

    def recent_calls(self, limit: int = 20) -> list[dict]:
        with self._lock:
            return list(self._calls[-limit:])

    # ---- 模拟「定时回刷持久层」(生产为独立任务每 30s 原子 UPDATE / Redis DEL) ----
    def persist(self, path: str) -> None:
        with self._lock:
            payload = {"tokens": {f"{p}::{pvd}": n for (p, pvd), n in self._tokens.items()}}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        os.replace(tmp, path)
