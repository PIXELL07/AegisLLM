from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DefenseDecision:
    """
    Result returned by a defense after inspecting a prompt.
    """

    allowed: bool
    reason: str = ""
    score: float | None = None


class Defense(ABC):
    """
    Base interface for prompt-level defenses.

    Defenses inspect an attack prompt before it reaches
    the target model.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name for the defense.
        """

        raise NotImplementedError

    @abstractmethod
    def inspect(
        self,
        prompt: str,
    ) -> DefenseDecision:
        """
        Inspect a prompt and decide whether it should
        be allowed to reach the target model.
        """

        raise NotImplementedError


class NoDefense(Defense):
    """
    Baseline defense that allows every prompt.

    This is useful when comparing defended execution
    against an equivalent no-defense baseline.
    """

    @property
    def name(self) -> str:
        return "none"

    def inspect(
        self,
        prompt: str,
    ) -> DefenseDecision:
        return DefenseDecision(
            allowed=True,
            reason="No defense applied.",
            score=0.0,
        )