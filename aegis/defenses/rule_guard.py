import re
from dataclasses import dataclass

from aegis.defenses.base import (
    Defense,
    DefenseDecision,
)


@dataclass(frozen=True)
class DefenseRule:
    """
    A single detection rule used by RuleBasedDefense.
    """

    name: str
    pattern: str
    weight: float = 1.0


DEFAULT_RULES = [
    DefenseRule(
        name="ignore_instructions",
        pattern=(
            r"\bignore\b.{0,40}"
            r"\b(previous|prior|above)\b.{0,20}"
            r"\b(instruction|instructions)\b"
        ),
    ),
    DefenseRule(
        name="system_override",
        pattern=(
            r"\b(system|developer)\b.{0,30}"
            r"\b(instruction|instructions|prompt)\b"
        ),
    ),
    DefenseRule(
        name="instruction_override",
        pattern=(
            r"\b(disregard|override|bypass)\b.{0,40}"
            r"\b(instruction|instructions|rules|policy|policies)\b"
        ),
    ),
    DefenseRule(
        name="role_reassignment",
        pattern=(
            r"\b(you are now|act as|pretend to be|roleplay as)\b"
        ),
    ),
    DefenseRule(
        name="jailbreak_language",
        pattern=(
            r"\b(jailbreak|developer mode|dan mode)\b"
        ),
    ),
    DefenseRule(
        name="priority_manipulation",
        pattern=(
            r"\b(highest priority|new priority|"
            r"supersede|takes precedence)\b"
        ),
    ),
]


class RuleBasedDefense(Defense):
    """
    Transparent rule-based prompt defense.

    Prompts are scored using configurable regex rules.
    The prompt is blocked when its accumulated score
    reaches the configured threshold.
    """

    def __init__(
        self,
        rules: list[DefenseRule] | None = None,
        threshold: float = 1.0,
    ) -> None:
        if threshold < 0:
            raise ValueError(
                "threshold must be non-negative."
            )

        self.rules = (
            list(rules)
            if rules is not None
            else list(DEFAULT_RULES)
        )

        self.threshold = threshold

    @property
    def name(self) -> str:
        return "rule_guard"

    def inspect(
        self,
        prompt: str,
    ) -> DefenseDecision:
        matched_rules: list[str] = []
        score = 0.0

        for rule in self.rules:
            if re.search(
                rule.pattern,
                prompt,
                flags=re.IGNORECASE | re.DOTALL,
            ):
                matched_rules.append(
                    rule.name
                )

                score += rule.weight

        allowed = score < self.threshold

        if matched_rules:
            reason = (
                "Matched defense rules: "
                + ", ".join(matched_rules)
            )
        else:
            reason = (
                "No defense rules matched."
            )

        return DefenseDecision(
            allowed=allowed,
            reason=reason,
            score=score,
        )