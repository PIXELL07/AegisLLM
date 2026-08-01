import argparse
import asyncio
from pathlib import Path

from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.encoding import EncodingAttack
from aegis.attacks.jailbreak import JailbreakAttack
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.csv_report import save_csv_report
from aegis.benchmark.metrics import attack_success_rate, category_metrics
from aegis.benchmark.report import build_report, save_report
from aegis.benchmark.runner import BenchmarkRunner
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.ollama import OllamaTarget


ATTACK_CLASSES = {
    "prompt_injection": PromptInjectionAttack,
    "jailbreak": JailbreakAttack,
    "encoding": EncodingAttack,
}

ALL_DATASETS = [
    "datasets/attacks/prompt_injection.json",
    "datasets/attacks/jailbreak.json",
    "datasets/attacks/encoding.json",
]


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
        "--dataset",
        default="datasets/attacks/prompt_injection.json",
        help="Attack dataset to run.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all available attack datasets.",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Save benchmark results to a JSON or CSV file.",
    )

    return parser.parse_args()


def build_attacks(dataset_path: str):
    attacks_data = load_attack_dataset(dataset_path)

    dataset_name = Path(dataset_path).stem

    if dataset_name not in ATTACK_CLASSES:
        raise ValueError(
            f"Unsupported attack dataset: {dataset_name}"
        )

    attack_class = ATTACK_CLASSES[dataset_name]

    return [
        attack_class(
            name=item["name"],
            prompt=item["prompt"],
            expected=item["expected"],
        )
        for item in attacks_data
    ]


def load_attacks(args):
    if args.all:
        attacks = []

        for dataset_path in ALL_DATASETS:
            attacks.extend(
                build_attacks(dataset_path)
            )

        return attacks

    return build_attacks(args.dataset)


async def main() -> None:
    args = parse_args()

    print("\nAegisLLM Security Benchmark")
    print("=" * 60)

    target = OllamaTarget(model=args.model)
    evaluator = ExactMatchEvaluator()

    attacks = load_attacks(args)

    runner = BenchmarkRunner(
        target=target,
        evaluator=evaluator,
    )

    results = []
    csv_results = []
    category_results = []

    print(f"Target Model  : {target.model_name}")

    if args.all:
        print("Attack Mode   : All categories")
    else:
        print(f"Dataset       : {args.dataset}")

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

        category_results.append(
            {
                "category": attack.category,
                "successful": result.successful,
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

    category_objects = [
        type(
            "CategoryResult",
            (),
            item,
        )()
        for item in category_results
    ]

    categories = category_metrics(
        category_objects
    )

    successful_attacks = sum(
        result.successful
        for result in results
    )

    print("\n")
    print("=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    print(f"Target Model        : {target.model_name}")
    print(f"Total Attacks       : {len(results)}")
    print(f"Successful Attacks  : {successful_attacks}")
    print(f"Attack Success Rate : {success_rate:.2%}")

    print("\nCategory Results")
    print("-" * 60)

    for category, metrics in categories.items():
        total = metrics["total_attacks"]
        successful = metrics["successful_attacks"]
        category_asr = metrics["attack_success_rate"]

        print(
            f"{category:<20} "
            f"{successful}/{total} successful "
            f"ASR: {category_asr:.2%}"
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
                attacks=attacks,
                results=results,
                success_rate=success_rate,
            )

            report["category_metrics"] = categories

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