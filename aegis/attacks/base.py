from abc import ABC, abstractmethod


class Attack(ABC):
    """Base interface for all AegisLLM attack plugins."""

    name: str
    category: str

    @abstractmethod
    def generate(self) -> str:
        """Generate an adversarial test prompt."""
        raise NotImplementedError