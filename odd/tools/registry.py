"""工具注册表。

维护 工具名称 -> Tool 实例 的映射，使 Agent 能在运行时动态查找并执行工具。
"""

from typing import Dict, List, Optional

from odd.tools.base import Tool


class ToolRegistry:
    """追踪可用的工具。"""

    def __init__(self):
        # 内部映射: 工具名称 -> Tool 实例。
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册一个工具实例。"""
        self._tools[tool.spec.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """按名称检索工具，未找到时返回 None。"""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """返回所有已注册的工具。"""
        return list(self._tools.values())

    def clear(self) -> None:
        """移除所有已注册的工具（测试时有用）。"""
        self._tools.clear()


# 应用使用的全局注册表实例。
registry = ToolRegistry()


def register(tool: Tool) -> Tool:
    """在全局注册表中注册工具实例的助手函数。

    可作为装饰器使用，或直接调用。
    """
    registry.register(tool)
    return tool
