from __future__ import annotations

from aegis.attacks.base import Attack


class PromptInjectionAttack(Attack):
    def __init__(
        self,
        name: str,
        prompt: str,
        expected: str,
    ) -> None:
        self._name = name
        self._prompt = prompt
        self._expected = expected

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return "prompt_injection"

    @property
    def expected(self) -> str:
        return self._expected

    def generate(self) -> str:
        return self._prompt