from aegis.attacks.base import Attack


class JailbreakAttack(Attack):
    """
    Represents a jailbreak attack against a language model.
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
        self.category = "jailbreak"

    def generate(self) -> str:
        return self.prompt