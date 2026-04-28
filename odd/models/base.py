"""模型提供者的抽象基类。"""

from abc import ABC, abstractmethod
from typing import List, Optional

from odd.types import ChatResponse, Message


class ModelProvider(ABC):
    """LLM 后端的接口。"""

    @abstractmethod
    def chat(
        self, messages: List[Message], tools: Optional[List[dict]] = None
    ) -> ChatResponse:
        """发送消息给模型并返回结构化响应。

        参数:
            messages: 对话历史。
            tools: 可选的工具定义列表，使用 OpenAI 兼容格式。
        """
        ...
