"""Anthropic model provider."""

from typing import List, Optional

from odd.config import config
from odd.models.base import ModelProvider
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class AnthropicProvider(ModelProvider):
    """Wrapper around Anthropic's Claude API."""

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

    def chat(self, messages: List[Message]) -> ChatResponse:
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

        resp = self.client.messages.create(**kwargs)

        content = ""
        tool_calls: List[ToolCall] = []
        for block in resp.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )
        return ChatResponse(content=content, tool_calls=tool_calls, raw=resp)


def _to_anthropic_msg(msg: Message) -> dict:
    """Convert internal Message to Anthropic message format."""
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
