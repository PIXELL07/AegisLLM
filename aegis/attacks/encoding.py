from aegis.attacks.base import Attack
from aegis.benchmark.risk import Severity


class EncodingAttack(Attack):
    """
    Represents an encoded or obfuscated instruction attack.
    """

    def __init__(
        self,
        name: str,
        prompt: str,
        expected: str,
        severity: Severity = Severity.MEDIUM,
    ):
        self.name = name
        self.prompt = prompt
        self.expected = expected
        self.severity = severity
        self.category = "encoding"

    def generate(self) -> str:
        return self.prompt