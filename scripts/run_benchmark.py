import argparse
import asyncio
import json
from pathlib import Path

from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.metrics import attack_success_rate
from aegis.benchmark.runner import BenchmarkRunner
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.ollama import OllamaTarget

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AegisLLM security benchmarks against an Ollama model."
    )

    parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="Ollama model to benchmark (default: llama3.2:3b)",
    )

    parser.add_argument(
        "--output",
        help="Path to save benchmark results as JSON",
    )

    return parser.parse_args()

    return parser.parse_args()

async def main() -> None:
    args = parse_args()
    print("\nAegisLLM Multi-Attack Benchmark")
    print("=" * 60)

    target = OllamaTarget(model=args.model)
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

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "model": target.model_name,
        "total_attacks": len(results),
        "successful_attacks": sum(
            result.successful for result in results
        ),
        "attack_success_rate": success_rate,
        "results": [
            {
                "attack": attack.name,
                "category": attack.category,
                "successful": result.successful,
                "score": result.score,
                "latency_ms": result.latency_ms,
                "response": result.response,
            }
            for attack, result in zip(attacks, results)
        ],
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nResults saved to: {output_path}")

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