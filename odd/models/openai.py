"""OpenAI model provider."""

from typing import List, Optional

from odd.config import config
from odd.models.base import ModelProvider
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class OpenAIProvider(ModelProvider):
    """Wrapper around OpenAI-compatible APIs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is required. Install it with: pip install openai"
            ) from exc

        self.client = OpenAI(
            api_key=api_key or config.openai_api_key,
            base_url=base_url or config.openai_base_url,
        )
        self.model = model or config.openai_model

    def chat(self, messages: List[Message]) -> ChatResponse:
        payload = [_to_openai_msg(m) for m in messages]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=payload,
        )
        choice = resp.choices[0]
        content = choice.message.content or ""
        tool_calls: List[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )
        return ChatResponse(content=content, tool_calls=tool_calls, raw=resp)


def _to_openai_msg(msg: Message) -> dict:
    """Convert internal Message to OpenAI chat format."""
    base = {"role": msg.role.value}
    if msg.role == MessageRole.TOOL:
        base["content"] = msg.content
        base["tool_call_id"] = msg.tool_call_id or ""
    else:
        base["content"] = msg.content
    if msg.tool_calls:
        base["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": str(tc.arguments)},
            }
            for tc in msg.tool_calls
        ]
    return base
