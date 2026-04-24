"""Odd 的工具系统。

提供 Tool 抽象基类、全局注册表以及 Agent 可调用的内置工具。
"""

from odd.tools.base import Tool, ToolSpec
from odd.tools.registry import register, registry

__all__ = ["Tool", "ToolSpec", "register", "registry"]
