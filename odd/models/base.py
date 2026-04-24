"""Abstract base class for model providers."""

from abc import ABC, abstractmethod
from typing import List

from odd.types import ChatResponse, Message


class ModelProvider(ABC):
    """Interface for LLM backends."""

    @abstractmethod
    def chat(self, messages: List[Message]) -> ChatResponse:
        """Send messages to the model and return a structured response."""
        ...
