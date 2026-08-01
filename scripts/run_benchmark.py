import asyncio

from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.metrics import attack_success_rate
from aegis.benchmark.runner import BenchmarkRunner
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.ollama import OllamaTarget


async def main() -> None:
    target = OllamaTarget(model="llama3.2:3b")

    evaluator = ExactMatchEvaluator()

    runner = BenchmarkRunner(
        target=target,
        evaluator=evaluator,
    )

    attack = PromptInjectionAttack()

    print("\nAegisLLM Benchmark")
    print("=" * 50)

    result = await runner.run(
        attack=attack,
        expected_marker="AEGIS_TEST_OVERRIDE",
    )

    print(f"Target Model : {result.target_model}")
    print(f"Attack       : {result.attack_name}")
    print(f"Category     : {result.attack_category}")
    print(f"Successful   : {result.successful}")
    print(f"Score        : {result.score:.2f}")
    print(f"Latency      : {result.latency_ms:.2f} ms")

    print("\nModel Response")
    print("-" * 50)
    print(result.response)

    asr = attack_success_rate([result])

    print("\nBenchmark Metrics")
    print("-" * 50)
    print(f"Attack Success Rate: {asr:.2%}")


if __name__ == "__main__":
    asyncio.run(main())