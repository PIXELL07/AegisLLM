from abc import ABC, abstractmethod


class Target(ABC):
    """Base interface for LLM targets evaluated by AegisLLM."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Send a prompt to the target model and return its response."""
        raise NotImplementedError