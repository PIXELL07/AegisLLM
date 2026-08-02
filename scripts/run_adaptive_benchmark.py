import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from aegis.adaptive.metrics import adaptive_metrics
from aegis.adaptive.runner import AdaptiveAttackRunner
from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.encoding import EncodingAttack
from aegis.attacks.jailbreak import JailbreakAttack
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.risk import Severity
from aegis.evaluators.contains import ContainsMatchEvaluator
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


EVALUATORS = {
    "exact": ExactMatchEvaluator,
    "contains": ContainsMatchEvaluator,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run adaptive AegisLLM security attacks "
            "against an Ollama model."
        )
    )

    parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help=(
            "Ollama model to benchmark "
            "(default: llama3.2:3b)."
        ),
    )

    parser.add_argument(
        "--dataset",
        default=(
            "datasets/attacks/"
            "prompt_injection.json"
        ),
        help="Attack dataset to run.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all available attack datasets.",
    )

    parser.add_argument(
        "--evaluator",
        choices=[
            "exact",
            "contains",
        ],
        default="exact",
        help=(
            "Evaluator used to determine attack "
            "success (default: exact)."
        ),
    )

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help=(
            "Maximum adaptive attempts per attack, "
            "including the original attempt "
            "(default: 5)."
        ),
    )

    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Optional path for saving the adaptive "
            "benchmark report as JSON."
        ),
    )

    return parser.parse_args()


def build_attacks(
    dataset_path: str,
):
    attacks_data = load_attack_dataset(
        dataset_path
    )

    dataset_name = Path(
        dataset_path
    ).stem

    if dataset_name not in ATTACK_CLASSES:
        raise ValueError(
            "Unsupported attack dataset: "
            f"{dataset_name}"
        )

    attack_class = ATTACK_CLASSES[
        dataset_name
    ]

    attacks = []

    for item in attacks_data:
        severity_value = item.get(
            "severity"
        )

        if severity_value is not None:
            severity = Severity(
                severity_value
            )

            attack = attack_class(
                name=item["name"],
                prompt=item["prompt"],
                expected=item["expected"],
                severity=severity,
            )

        else:
            attack = attack_class(
                name=item["name"],
                prompt=item["prompt"],
                expected=item["expected"],
            )

        attacks.append(
            attack
        )

    return attacks


def load_attacks(
    args,
):
    if args.all:
        attacks = []

        for dataset_path in ALL_DATASETS:
            attacks.extend(
                build_attacks(
                    dataset_path
                )
            )

        return attacks

    return build_attacks(
        args.dataset
    )


def build_evaluator(
    name: str,
):
    if name not in EVALUATORS:
        raise ValueError(
            f"Unsupported evaluator: {name}"
        )

    return EVALUATORS[name]()


def build_report(
    model_name,
    evaluator_name,
    max_attempts,
    attacks,
    results,
    metrics,
):
    return {
        "model": model_name,
        "evaluator": evaluator_name,
        "adaptive": True,
        "max_attempts": max_attempts,
        "total_attacks": len(attacks),
        "metrics": metrics,
        "results": [
            asdict(result)
            for result in results
        ],
    }


def save_report(
    report,
    output,
):
    output_path = Path(
        output
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )


async def main() -> None:
    args = parse_args()

    if args.max_attempts < 1:
        raise ValueError(
            "--max-attempts must be at least 1."
        )

    target = OllamaTarget(
        model=args.model
    )

    evaluator = build_evaluator(
        args.evaluator
    )

    attacks = load_attacks(
        args
    )

    runner = AdaptiveAttackRunner(
        target=target,
        evaluator=evaluator,
        max_attempts=args.max_attempts,
    )

    results = []

    print()
    print(
        "AegisLLM Adaptive Attack Benchmark"
    )
    print("=" * 60)

    print(
        f"Target Model  : "
        f"{target.model_name}"
    )

    print(
        f"Evaluator     : "
        f"{args.evaluator}"
    )

    if args.all:
        print(
            "Attack Mode   : All categories"
        )
    else:
        print(
            f"Dataset       : {args.dataset}"
        )

    print(
        f"Total Attacks : {len(attacks)}"
    )

    print(
        f"Max Attempts  : "
        f"{args.max_attempts}"
    )

    print("=" * 60)

    for index, attack in enumerate(
        attacks,
        start=1,
    ):
        print()
        print(
            f"[{index}/{len(attacks)}] "
            f"Running: {attack.name}"
        )

        result = await runner.run(
            attack,
            attack.expected,
        )

        results.append(
            result
        )

        print(
            f"Attack      : {attack.name}"
        )

        print(
            f"Category    : {attack.category}"
        )

        print(
            f"Severity    : "
            f"{attack.severity.value}"
        )

        print(
            f"Successful  : "
            f"{result.successful}"
        )

        print(
            f"Attempts    : "
            f"{result.attempts_used}"
        )

        strategy = (
            result.successful_strategy
            if result.successful_strategy
            is not None
            else "none"
        )

        print(
            f"Strategy    : {strategy}"
        )

        print()
        print("Attempt History")
        print("-" * 60)

        for attempt in (
            result.attempt_history
        ):
            status = (
                "SUCCESS"
                if attempt.successful
                else "FAILED"
            )

            print(
                f"Attempt "
                f"{attempt.attempt:<2} "
                f"{attempt.strategy:<18} "
                f"{status:<8} "
                f"{attempt.latency_ms:.2f} ms"
            )

    metrics = adaptive_metrics(
        results
    )

    print()
    print("=" * 60)
    print(
        "Adaptive Benchmark Summary"
    )
    print("=" * 60)

    print(
        f"Target Model                : "
        f"{target.model_name}"
    )

    print(
        f"Evaluator                   : "
        f"{args.evaluator}"
    )

    print(
        f"Total Attacks               : "
        f"{metrics['total_attacks']}"
    )

    print(
        f"Original Successful Attacks : "
        f"{metrics['original_successes']}"
    )

    print(
        f"Adaptive Successful Attacks : "
        f"{metrics['adaptive_successes']}"
    )

    print(
        f"Original ASR                : "
        f"{metrics['original_asr']:.2%}"
    )

    print(
        f"Adaptive ASR                : "
        f"{metrics['adaptive_asr']:.2%}"
    )

    print(
        f"Adaptive Gain               : "
        f"{metrics['adaptive_gain']:+.2%}"
    )

    print(
        f"Average Attempts            : "
        f"{metrics['average_attempts']:.2f}"
    )

    print(
        f"Average Attempts to Success : "
        f"{metrics['average_attempts_to_success']:.2f}"
    )
    print()
    print("Category Adaptive Results")
    print("-" * 60)

    print(
        f"{'Category':<20}"
        f"{'Original':>12}"
        f"{'Adaptive':>12}"
        f"{'Gain':>12}"
    )

    print("-" * 60)

    for category, category_data in (
        metrics["category_metrics"].items()
    ):
        print(
            f"{category:<20}"
            f"{category_data['original_asr']:>11.2%}"
            f"{category_data['adaptive_asr']:>12.2%}"
            f"{category_data['adaptive_gain']:>+12.2%}"
    )

    print()
    print("Successful Strategies")
    print("-" * 60)

    strategy_successes = metrics[
        "strategy_successes"
    ]

    if strategy_successes:
        for strategy, count in (
            strategy_successes.items()
        ):
            print(
                f"{strategy:<24}: {count}"
            )
    else:
        print("None")

    print("=" * 60)

    if args.output:
        report = build_report(
            model_name=target.model_name,
            evaluator_name=args.evaluator,
            max_attempts=args.max_attempts,
            attacks=attacks,
            results=results,
            metrics=metrics,
        )

        save_report(
            report,
            args.output,
        )

        print()
        print(
            f"Results saved to: "
            f"{args.output}"
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )