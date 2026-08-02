from dataclasses import dataclass, field
from typing import Any

from aegis.adaptive.mutators import (
    AttackMutator,
    get_default_mutators,
)


@dataclass
class AdaptiveAttempt:
    """
    A single attempt made during an adaptive attack.
    """

    attempt: int
    strategy: str
    prompt: str
    response: str
    successful: bool
    score: float
    latency_ms: float


@dataclass
class AdaptiveAttackResult:
    """
    Complete result of an adaptive attack run.
    """

    attack: str
    category: str
    successful: bool
    attempts_used: int
    successful_attempt: int | None
    successful_strategy: str | None
    final_score: float
    final_response: str
    attempt_history: list[AdaptiveAttempt] = field(
        default_factory=list
    )


class AdaptiveAttackRunner:
    """
    Execute an attack and progressively mutate it when
    previous attempts fail.
    """

    def __init__(
        self,
        target: Any,
        evaluator: Any,
        mutators: list[AttackMutator] | None = None,
        max_attempts: int | None = None,
    ) -> None:
        self.target = target
        self.evaluator = evaluator

        self.mutators = (
            mutators
            if mutators is not None
            else get_default_mutators()
        )

        if max_attempts is None:
            max_attempts = len(self.mutators) + 1

        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        self.max_attempts = max_attempts

    async def _call_target(
        self,
        prompt: str,
    ) -> tuple[str, float]:
        """
        Send a prompt to the configured async target and
        measure request latency.
        """

        import time

        start = time.perf_counter()

        response = await self.target.generate(
            prompt
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return str(response), latency_ms

    def _evaluate(
        self,
        response: str,
        expected_marker: str,
    ) -> tuple[bool, float]:
        """
        Evaluate a target response against the attack's
        expected marker.
        """

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
    ) -> AdaptiveAttackResult:
        """
        Execute one adaptive attack.

        Attempt 1 uses the original prompt.
        Later attempts use mutation strategies in order.
        Execution stops when an attempt succeeds.
        """

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

        original_prompt = getattr(
            attack,
            "prompt",
            None,
        )

        if original_prompt is None:
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

        history: list[AdaptiveAttempt] = []

        total_possible_attempts = min(
            self.max_attempts,
            len(self.mutators) + 1,
        )

        for attempt_number in range(
            1,
            total_possible_attempts + 1,
        ):
            if attempt_number == 1:
                strategy = "original"
                prompt = original_prompt

            else:
                mutator = self.mutators[
                    attempt_number - 2
                ]

                strategy = mutator.name

                prompt = mutator.mutate(
                    original_prompt,
                    attempt=attempt_number,
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

            attempt = AdaptiveAttempt(
                attempt=attempt_number,
                strategy=strategy,
                prompt=prompt,
                response=response,
                successful=successful,
                score=score,
                latency_ms=latency_ms,
            )

            history.append(attempt)

            if successful:
                return AdaptiveAttackResult(
                    attack=attack_name,
                    category=category,
                    successful=True,
                    attempts_used=len(history),
                    successful_attempt=attempt_number,
                    successful_strategy=strategy,
                    final_score=score,
                    final_response=response,
                    attempt_history=history,
                )

        final_attempt = history[-1]

        return AdaptiveAttackResult(
            attack=attack_name,
            category=category,
            successful=False,
            attempts_used=len(history),
            successful_attempt=None,
            successful_strategy=None,
            final_score=final_attempt.score,
            final_response=final_attempt.response,
            attempt_history=history,
        )