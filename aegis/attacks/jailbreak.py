from aegis.attacks.base import Attack
from aegis.benchmark.risk import Severity


class JailbreakAttack(Attack):
    """
    Represents a jailbreak attack against a language model.
    """

    def __init__(
        self,
        name: str,
        prompt: str,
        expected: str,
        severity: Severity = Severity.CRITICAL,
    ):
        self.name = name
        self.prompt = prompt
        self.expected = expected
        self.severity = severity
        self.category = "jailbreak"

    def generate(self) -> str:
        return self.prompt