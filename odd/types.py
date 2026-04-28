"""Odd 的核心数据类型。"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ToolCall:
    """表示模型请求的工具调用。"""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class Message:
    """对话中的单条消息。"""

    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # tool name for tool role


@dataclass
class ChatResponse:
    """来自模型提供者的结构化响应。"""

    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    thinking: Optional[str] = None  # 模型推理 / 思维链
    raw: Optional[Any] = None  # 提供者特定的原始响应
