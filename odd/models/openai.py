"""OpenAI 模型提供者。"""

import json
from typing import List, Optional

from odd.config import config
from odd.models.base import ModelProvider
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class OpenAIProvider(ModelProvider):
    """OpenAI 兼容 API 的封装。"""

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

    def chat(
        self, messages: List[Message], tools: Optional[List[dict]] = None
    ) -> ChatResponse:
        payload = [_to_openai_msg(m) for m in messages]
        kwargs: dict = {
            "model": self.model,
            "messages": payload,
        }
        if tools:
            kwargs["tools"] = tools
        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        content = choice.message.content or ""
        thinking = getattr(choice.message, "reasoning_content", None)
        tool_calls: List[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )
        return ChatResponse(
            content=content,
            tool_calls=tool_calls,
            thinking=thinking,
            raw=resp,
        )


def _to_openai_msg(msg: Message) -> dict:
    """将内部 Message 转换为 OpenAI 聊天格式。"""
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
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
            }
            for tc in msg.tool_calls
        ]
    return base
