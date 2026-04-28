"""最小化配置管理。"""

import os
from dataclasses import dataclass


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


@dataclass(frozen=True)
class Config:
    """从环境变量加载的运行时配置。"""

    openai_api_key: str = _env("OPENAI_API_KEY", '')
    openai_base_url: str = _env("OPENAI_BASE_URL", "https://api.minimaxi.com/v1")
    openai_model: str = _env("OPENAI_MODEL", "MiniMax-M2.7")

    anthropic_api_key: str = _env("ANTHROPIC_API_KEY", '')
    anthropic_base_url: str = _env("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
    anthropic_model: str = _env("ANTHROPIC_MODEL", "MiniMax-M2.7")

    default_provider: str = _env("ODD_DEFAULT_PROVIDER", "openai")

    @classmethod
    def from_env(cls) -> "Config":
        return cls()


# 全局单例；需要时可在导入时重新加载。
config = Config.from_env()
