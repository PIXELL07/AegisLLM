from aegis.attacks.base import Attack


class EncodingAttack(Attack):
    """
    Represents an encoded or obfuscated instruction attack.
    """

    def __init__(
        self,
        name: str,
        prompt: str,
        expected: str,
    ):
        self.name = name
        self.prompt = prompt
        self.expected = expected
        self.category = "encoding"

    def generate(self) -> str:
        return self.prompt