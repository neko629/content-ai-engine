"""模型/用途配置加载。

设计要点（与生产一致）：
- 供应商与模型完全数据化（config/models.json），不在代码里硬编码；
- 一个业务「用途」（标题/审核/文生图提示词…）映射一组候选模型，换模型不改业务代码；
- api_key 只经环境变量注入，永不写进仓库。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(_ROOT, "config", "models.json")


@dataclass
class ModelConfig:
    name: str
    provider: str                       # openai_compatible | mock
    model: str
    base_url_env: Optional[str] = None
    api_key_env: Optional[str] = None
    load_balance: bool = False
    is_default: bool = False

    def base_url(self) -> Optional[str]:
        if not self.base_url_env:
            return None
        return os.environ.get(self.base_url_env)

    def api_key(self) -> Optional[str]:
        if not self.api_key_env:
            return None
        return os.environ.get(self.api_key_env)


@dataclass
class EngineConfig:
    models: list[ModelConfig] = field(default_factory=list)
    purposes: dict[str, list[str]] = field(default_factory=dict)   # 用途 -> 候选模型名(有序)
    fail_open_on_llm_error: bool = True


def load(path: Optional[str] = None) -> EngineConfig:
    path = path or os.environ.get("AIENGINE_CONFIG") or DEFAULT_CONFIG_PATH
    with open(path, encoding="utf-8") as fh:
        raw: dict[str, Any] = json.load(fh)
    models = [ModelConfig(**m) for m in raw.get("models", [])]
    engine_cfg = raw.get("engine", {})
    return EngineConfig(
        models=models,
        purposes=raw.get("purposes", {}),
        fail_open_on_llm_error=bool(engine_cfg.get("fail_open_on_llm_error", True)),
    )
