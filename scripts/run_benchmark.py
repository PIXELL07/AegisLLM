import argparse
import asyncio

from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.csv_report import save_csv_report
from aegis.benchmark.metrics import attack_success_rate
from aegis.benchmark.report import build_report, save_report
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
        default=None,
        help="Save benchmark results to a JSON or CSV file.",
    )

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
    csv_results = []

    print(f"Target Model  : {target.model_name}")
    print(f"Total Attacks : {len(attacks)}")
    print("=" * 60)

    for index, attack in enumerate(attacks, start=1):
        print(
            f"\n[{index}/{len(attacks)}] "
            f"Running: {attack.name}"
        )

        result = await runner.run(
            attack,
            attack.expected,
        )

        results.append(result)

        csv_results.append(
            {
                "attack": attack.name,
                "category": attack.category,
                "result": result,
            }
        )

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

    successful_attacks = sum(
        result.successful
        for result in results
    )

    print(
        f"Successful Attacks  : "
        f"{successful_attacks}"
    )

    print(
        f"Attack Success Rate : "
        f"{success_rate:.2%}"
    )

    print("=" * 60)

    if args.output:
        if args.output.lower().endswith(".csv"):
            save_csv_report(
                results=csv_results,
                output_path=args.output,
            )

        else:
            report = build_report(
                model=target.model_name,
                results=results,
            )

            save_report(
                report,
                args.output,
            )

        print(
            f"\nResults saved to: "
            f"{args.output}"
        )


if __name__ == "__main__":
    asyncio.run(main())