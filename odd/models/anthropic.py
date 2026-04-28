"""Anthropic 模型提供者。"""

from typing import List, Optional

from odd.config import config
from odd.models.base import ModelProvider
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class AnthropicProvider(ModelProvider):
    """Anthropic Claude API 的封装。"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required. Install it with: pip install anthropic"
            ) from exc

        self.client = Anthropic(
            api_key=api_key or config.anthropic_api_key,
            base_url=base_url or config.anthropic_base_url,
        )
        self.model = model or config.anthropic_model

    def chat(
        self, messages: List[Message], tools: Optional[List[dict]] = None
    ) -> ChatResponse:
        system_msg = ""
        convo: List[dict] = []
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                system_msg = m.content
            else:
                convo.append(_to_anthropic_msg(m))

        kwargs: dict = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": convo,
        }
        if system_msg:
            kwargs["system"] = system_msg
        if tools:
            kwargs["tools"] = [_to_anthropic_tool(t) for t in tools]

        resp = self.client.messages.create(**kwargs)

        content = ""
        thinking_parts: List[str] = []
        tool_calls: List[ToolCall] = []
        for block in resp.content:
            if block.type == "text":
                content += block.text
            elif block.type == "thinking":
                thinking_parts.append(block.thinking)
            elif block.type == "redacted_thinking":
                thinking_parts.append("[redacted thinking]")
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )
        return ChatResponse(
            content=content,
            tool_calls=tool_calls,
            thinking="\n".join(thinking_parts) if thinking_parts else None,
            raw=resp,
        )


def _to_anthropic_msg(msg: Message) -> dict:
    """将内部 Message 转换为 Anthropic 消息格式。"""
    if msg.role == MessageRole.TOOL:
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id or "",
                    "content": msg.content,
                }
            ],
        }

    if msg.role == MessageRole.ASSISTANT and msg.tool_calls:
        content_blocks: List[dict] = []
        if msg.content:
            content_blocks.append({"type": "text", "text": msg.content})
        for tc in msg.tool_calls:
            content_blocks.append(
                {
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.name,
                    "input": tc.arguments,
                }
            )
        return {"role": "assistant", "content": content_blocks}

    return {"role": msg.role.value, "content": msg.content}


def _to_anthropic_tool(tool: dict) -> dict:
    """将 OpenAI 格式工具转换为 Anthropic 格式。"""
    func = tool.get("function", {})
    return {
        "name": func.get("name", ""),
        "description": func.get("description", ""),
        "input_schema": func.get("parameters", {}),
    }
