"""工具的抽象基类。

Tool 是暴露给 Agent 的离散能力。每个工具需声明规格（名称、描述、
JSON Schema 参数）并实现 execute() 方法，接收参数字典并返回字符串结果。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ToolSpec:
    """类 JSON Schema 的工具描述。

    属性:
        name: 模型调用工具时使用的唯一标识符。
        description: 人类可读的工具功能说明。
        parameters: 描述期望参数的 JSON Schema 对象。
    """

    name: str
    description: str
    parameters: Dict[str, Any]


class Tool(ABC):
    """暴露给 Agent 的可调用能力。"""

    @property
    @abstractmethod
    def spec(self) -> ToolSpec:
        """返回供模型消费的工具规格。"""
        ...

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> str:
        """使用给定参数执行工具。

        参数:
            arguments: 与工具参数模式匹配的已解析 JSON 对象。

        返回:
            字符串结果（通常为 JSON），将回传给模型。
        """
        ...
