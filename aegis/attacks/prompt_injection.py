from aegis.attacks.base import Attack
from aegis.benchmark.risk import Severity


class PromptInjectionAttack(Attack):
    """
    Represents a prompt injection attack against a language model.
    """

    def __init__(
        self,
        name: str,
        prompt: str,
        expected: str,
        severity: Severity = Severity.HIGH,
    ):
        self.name = name
        self.prompt = prompt
        self.expected = expected
        self.severity = severity
        self.category = "prompt_injection"

    def generate(self) -> str:
        return self.prompt