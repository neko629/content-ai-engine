"""封面生成：标题 → SD 提示词 → 文生图 → 标记回写（参考实现）。

流程镜像生产批量封面链：
1. 标题交给 LLM 扩写成更适合文生图的英文/结构提示词（``generate_sd_prompt``），
   结果带 Redis 式缓存（这里用进程内 dict 演示），失败不写缓存；
2. 建"生成任务"并**不等结果立即返回**——生产里这一步是 Celery 异步提交；
   任务完成由统一收敛点触发回写钩子，把产出物写回内容条目（``_cover_for_item`` 标记）；
3. mock 图片源保证离线可跑；配 ``IMG_ENDPOINT``（返回 ``{"b64_json": ...}``）即走真文生图。
"""
from __future__ import annotations

import hashlib
import time
import uuid

from .gateway import LLMGateway
from .images import b64_data_uri, generate_cover
from .json_repair import extract_json

_SD_CACHE_TTL_S = 24 * 3600  # 生产为 Redis：key=md5(seed)，TTL 24h


class SDCache:
    """进程内提示词缓存。对外语义与生产 Redis 缓存一致。"""

    def __init__(self, ttl: int = _SD_CACHE_TTL_S) -> None:
        self._ttl = ttl
        self._store: dict[str, tuple[float, dict]] = {}

    def get(self, key: str):
        hit = self._store.get(key)
        if not hit:
            return None
        ts, value = hit
        if time.time() - ts > self._ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: dict) -> None:
        self._store[key] = (time.time(), value)


class CoverService:
    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway
        self._cache = SDCache()
        self._tasks: dict[str, dict] = {}

    def generate_sd_prompt(self, seed_text: str) -> dict:
        """标题 → 文生图提示词（LLM 扩写 + 缓存）。"""
        key = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
        cached = self._cache.get(key)
        if cached is not None:
            return {**cached, "cached": True}

        messages = [
            {"role": "system", "content": "把下面的内容主题扩写成文生图英文提示词。"
                                          '只输出 JSON：{"prompt": "...", "negative_prompt": "..."}'},
            {"role": "user", "content": seed_text},
        ]
        comp = self._gateway.call("sd_prompt", messages, temperature=0.4, json_mode=True)
        data, _ = extract_json(comp.content)
        prompt = (data or {}).get("prompt", "") if isinstance(data, dict) else ""
        negative = (data or {}).get("negative_prompt", "") if isinstance(data, dict) else ""
        if not prompt:
            prompt = seed_text  # 兜底：不给空提示词
        result = {"prompt": prompt, "negative_prompt": negative, "cached": False}
        self._cache.set(key, {"prompt": prompt, "negative_prompt": negative})
        return result

    def submit_cover(self, item_id: int, title: str) -> dict:
        """建一个封面生成任务，返回后立即结束（生产为异步提交，进度走轮询）。"""
        if not (title or "").strip():
            return {"status": "skipped", "reason": "empty title"}

        try:
            sd = self.generate_sd_prompt(f"封面：{title}")
        except Exception as exc:  # noqa: BLE001 —— 单条失败不拖垮批量
            return {"status": "failed", "reason": f"sd_prompt error: {exc}"}

        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {"status": "RUNNING", "item_id": item_id, "created": time.time()}

        # ---- mock 立即完成；生产为 submit -> watch(45s轮询) -> recover_stuck 兜底 ----
        try:
            image_format, payload = generate_cover(sd["prompt"] or f"封面：{title}")
            data_uri = b64_data_uri(image_format, payload)
        except Exception as exc:  # noqa: BLE001
            self._tasks[task_id]["status"] = "FAILED"
            return {"status": "failed", "reason": f"text2img error: {exc}"}

        self._tasks[task_id].update({"status": "COMPLETED", "finished": time.time()})
        return {
            "status": "ok",
            "task_id": task_id,
            "marker": f"_cover_for_item:{item_id}",   # 完成钩子据标记回写，见 pipeline
            "cover_data_uri": data_uri,
            "sd_prompt": sd["prompt"],
            "sd_cached": sd["cached"],
        }
