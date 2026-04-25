"""Abstract base class for model providers."""

from abc import ABC, abstractmethod
from typing import List, Optional

from odd.types import ChatResponse, Message


class ModelProvider(ABC):
    """Interface for LLM backends."""

    @abstractmethod
    def chat(
        self, messages: List[Message], tools: Optional[List[dict]] = None
    ) -> ChatResponse:
        """Send messages to the model and return a structured response.

        Args:
            messages: Conversation history.
            tools: Optional list of tool definitions in OpenAI-compatible format.
        """
        ...
