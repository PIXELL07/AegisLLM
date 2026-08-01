import time

from aegis.attacks.base import Attack
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.schemas.result import AttackResult
from aegis.targets.base import Target


class BenchmarkRunner:
    """Coordinates attack generation, model execution, and evaluation."""

    def __init__(
        self,
        target: Target,
        evaluator: ExactMatchEvaluator,
    ):
        self.target = target
        self.evaluator = evaluator

    async def run(
        self,
        attack: Attack,
        expected_marker: str,
    ) -> AttackResult:

        prompt = attack.generate()

        start_time = time.perf_counter()

        response = await self.target.generate(prompt)

        latency_ms = (time.perf_counter() - start_time) * 1000

        successful, score = self.evaluator.evaluate(
            response=response,
            expected_marker=expected_marker,
        )

        return AttackResult(
            attack_name=attack.name,
            attack_category=attack.category,
            prompt=prompt,
            response=response,
            successful=successful,
            score=score,
            latency_ms=latency_ms,
            target_model=self.target.model_name,
        )