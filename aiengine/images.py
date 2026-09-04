"""占位封面生成：零依赖、纯标准库画一张可辨识的 PNG。

生产环境这里替换为「文生图供应商任务 + 轮询取图」，本模块仅保证
demo 离线也能看到「封面已生成」的实物。配了 ``IMG_ENDPOINT`` 环境变量
（任意返回 ``{"b64_json": ...}`` 的文生图 HTTP 服务）时自动切真模型。
"""
from __future__ import annotations

import base64
import hashlib
import os
import struct
import urllib.request
import zlib

COLORS = [
    (72, 118, 255), (160, 60, 220), (30, 144, 160), (222, 92, 120),
    (60, 130, 90), (214, 137, 16),
]


def _gradient_png_bytes(width: int, height: int, seed_text: str) -> bytes:
    palette_idx = int(hashlib.md5(seed_text.encode("utf-8")).digest()[0]) % len(COLORS)
    top, bottom = COLORS[palette_idx], COLORS[(palette_idx + 1) % len(COLORS)]
    rows = bytearray()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        row = bytearray([0])                     # PNG filter: None
        for x in range(width):
            # 棋盘格叠加，让不同标题生成的图肉眼可区分
            shade = 1.0 if ((x // 32) + (y // 32)) % 2 else 0.82
            row += bytes((int(r * shade), int(g * shade), int(b * shade)))
        rows += row

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)   # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(rows), 6))
        + chunk(b"IEND", b"")
    )


def generate_cover(seed_text: str, width: int = 480, height: int = 320) -> tuple[str, bytes]:
    """返回 (mime_or_endpoint, bytes)。有 IMG_ENDPOINT 时走后端真文生图，否则占位 PNG。"""
    endpoint = os.environ.get("IMG_ENDPOINT")
    if endpoint:
        import json

        payload = json.dumps({"prompt": seed_text, "width": width, "height": height}).encode()
        req = urllib.request.Request(endpoint, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 (demo)
            data = json.loads(resp.read().decode("utf-8"))
        b64 = (data.get("b64_json") or data.get("image") or "").strip()
        if b64:
            return endpoint, base64.b64decode(b64)
    return "png", _gradient_png_bytes(width, height, seed_text)


def b64_data_uri(image_format: str, payload: bytes) -> str:
    mime = image_format if image_format != "png" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(payload).decode('ascii')}"
