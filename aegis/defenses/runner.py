import time
from dataclasses import dataclass
from typing import Any

from aegis.defenses.base import (
    Defense,
    DefenseDecision,
)


@dataclass
class DefenseBenchmarkResult:
    """
    Result of running one attack through a defense.
    """

    attack: str
    category: str
    defense: str

    blocked: bool
    defense_reason: str
    defense_score: float | None

    successful: bool
    score: float

    response: str
    latency_ms: float


class DefenseBenchmarkRunner:
    """
    Run attacks through a defense before they reach
    the target model.
    """

    def __init__(
        self,
        target: Any,
        evaluator: Any,
        defense: Defense,
    ) -> None:
        self.target = target
        self.evaluator = evaluator
        self.defense = defense

    async def _call_target(
        self,
        prompt: str,
    ) -> tuple[str, float]:
        start = time.perf_counter()

        response = await self.target.generate(
            prompt
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return (
            str(response),
            latency_ms,
        )

    def _evaluate(
        self,
        response: str,
        expected_marker: str,
    ) -> tuple[bool, float]:
        result = self.evaluator.evaluate(
            response,
            expected_marker,
        )

        if isinstance(result, tuple):
            successful, score = result

            return (
                bool(successful),
                float(score),
            )

        if isinstance(result, bool):
            return (
                result,
                1.0 if result else 0.0,
            )

        successful = getattr(
            result,
            "successful",
            None,
        )

        if successful is None:
            raise ValueError(
                "Evaluator result must be a tuple, bool, "
                "or contain a successful attribute."
            )

        score = getattr(
            result,
            "score",
            1.0 if successful else 0.0,
        )

        return (
            bool(successful),
            float(score),
        )

    async def run(
        self,
        attack: Any,
        expected_marker: str | None = None,
    ) -> DefenseBenchmarkResult:
        attack_name = getattr(
            attack,
            "name",
            "unknown",
        )

        category = getattr(
            attack,
            "category",
            "unknown",
        )

        prompt = getattr(
            attack,
            "prompt",
            None,
        )

        if prompt is None:
            raise ValueError(
                "Attack must contain a prompt attribute."
            )

        if expected_marker is None:
            expected_marker = getattr(
                attack,
                "expected",
                None,
            )

        if expected_marker is None:
            raise ValueError(
                "Attack must contain an expected marker."
            )

        decision: DefenseDecision = (
            self.defense.inspect(
                prompt
            )
        )

        if not decision.allowed:
            return DefenseBenchmarkResult(
                attack=attack_name,
                category=category,
                defense=self.defense.name,
                blocked=True,
                defense_reason=decision.reason,
                defense_score=decision.score,
                successful=False,
                score=0.0,
                response="",
                latency_ms=0.0,
            )

        response, latency_ms = (
            await self._call_target(
                prompt
            )
        )

        successful, score = (
            self._evaluate(
                response,
                expected_marker,
            )
        )

        return DefenseBenchmarkResult(
            attack=attack_name,
            category=category,
            defense=self.defense.name,
            blocked=False,
            defense_reason=decision.reason,
            defense_score=decision.score,
            successful=successful,
            score=score,
            response=response,
            latency_ms=latency_ms,
        )