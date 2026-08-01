import pytest

from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.metrics import attack_success_rate
from aegis.benchmark.runner import BenchmarkRunner
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.base import Target


class MockTarget(Target):
    @property
    def model_name(self) -> str:
        return "mock-model"

    async def generate(self, prompt: str) -> str:
        return "AEGIS_TEST_OVERRIDE"


@pytest.mark.asyncio
async def test_benchmark_runner():
    target = MockTarget()
    evaluator = ExactMatchEvaluator()
    attack = PromptInjectionAttack()

    runner = BenchmarkRunner(
        target=target,
        evaluator=evaluator,
    )

    result = await runner.run(
        attack=attack,
        expected_marker="AEGIS_TEST_OVERRIDE",
    )

    assert result.successful is True
    assert result.score == 1.0
    assert result.target_model == "mock-model"
    assert result.attack_category == "prompt_injection"
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_attack_success_rate():
    target = MockTarget()
    evaluator = ExactMatchEvaluator()
    attack = PromptInjectionAttack()

    runner = BenchmarkRunner(target, evaluator)

    result = await runner.run(
        attack,
        expected_marker="AEGIS_TEST_OVERRIDE",
    )

    assert attack_success_rate([result]) == 1.0


def test_empty_attack_success_rate():
    assert attack_success_rate([]) == 0.0