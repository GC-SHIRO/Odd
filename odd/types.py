"""Core data types for Odd."""

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
    """Represents a tool invocation requested by the model."""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class Message:
    """A single message in the conversation."""

    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # tool name for tool role


@dataclass
class ChatResponse:
    """Structured response from a model provider."""

    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw: Optional[Any] = None  # provider-specific raw response
