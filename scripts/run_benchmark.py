import asyncio

from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.metrics import attack_success_rate
from aegis.benchmark.runner import BenchmarkRunner
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.ollama import OllamaTarget


async def main() -> None:
    print("\nAegisLLM Multi-Attack Benchmark")
    print("=" * 60)

    target = OllamaTarget(model="llama3.2:3b")
    evaluator = ExactMatchEvaluator()

    attacks_data = load_attack_dataset(
        "datasets/attacks/prompt_injection.json"
    )

    attacks = [
        PromptInjectionAttack(
            name=item["name"],
            prompt=item["prompt"],
            expected=item["expected"],
        )
        for item in attacks_data
    ]

    runner = BenchmarkRunner(
        target=target,
        evaluator=evaluator,
    )

    results = []

    print(f"Target Model  : {target.model_name}")
    print(f"Total Attacks : {len(attacks)}")
    print("=" * 60)

    for index, attack in enumerate(attacks, start=1):
        print(f"\n[{index}/{len(attacks)}] Running: {attack.name}")

        result = await runner.run(
            attack,
            attack.expected,
        )
        results.append(result)

        print(f"Attack     : {attack.name}")
        print(f"Category   : {attack.category}")
        print(f"Successful : {result.successful}")
        print(f"Score      : {result.score}")
        print(f"Latency    : {result.latency_ms:.2f} ms")

        print("\nModel Response")
        print("-" * 60)
        print(result.response)

    success_rate = attack_success_rate(results)

    print("\n")
    print("=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    print(f"Target Model        : {target.model_name}")
    print(f"Total Attacks       : {len(results)}")
    print(
        f"Successful Attacks  : "
        f"{sum(result.successful for result in results)}"
    )
    print(f"Attack Success Rate : {success_rate:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())