import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.encoding import EncodingAttack
from aegis.attacks.jailbreak import JailbreakAttack
from aegis.attacks.prompt_injection import PromptInjectionAttack
from aegis.benchmark.risk import Severity
from aegis.defenses.base import NoDefense
from aegis.defenses.benign import benign_metrics
from aegis.defenses.metrics import defense_metrics
from aegis.defenses.rule_guard import RuleBasedDefense
from aegis.defenses.runner import DefenseBenchmarkRunner
from aegis.evaluators.contains import ContainsMatchEvaluator
from aegis.evaluators.evaluator import ExactMatchEvaluator
from aegis.targets.ollama import OllamaTarget
from aegis.taxonomy.owasp import get_security_risk_dict


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


DEFAULT_BENIGN_DATASET = (
    "datasets/benign/prompts.json"
)


EVALUATORS = {
    "exact": ExactMatchEvaluator,
    "contains": ContainsMatchEvaluator,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare baseline and defended AegisLLM "
            "security benchmarks against an Ollama model."
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
        "--defense",
        choices=[
            "rule_guard",
        ],
        default="rule_guard",
        help=(
            "Defense to benchmark "
            "(default: rule_guard)."
        ),
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help=(
            "Detection threshold for rule_guard "
            "(default: 1.0)."
        ),
    )

    parser.add_argument(
        "--benign-dataset",
        default=DEFAULT_BENIGN_DATASET,
        help=(
            "Benign prompt dataset used to measure "
            "false-positive behavior."
        ),
    )

    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Optional path for saving the defense "
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


def build_defense(
    name: str,
    threshold: float = 1.0,
):
    if name == "rule_guard":
        return RuleBasedDefense(
            threshold=threshold
        )

    if name == "none":
        return NoDefense()

    raise ValueError(
        f"Unsupported defense: {name}"
    )


def load_benign_prompts(
    dataset_path: str,
):
    path = Path(
        dataset_path
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(
            file
        )

    if not isinstance(
        data,
        list,
    ):
        raise ValueError(
            "Benign dataset must contain "
            "a JSON list."
        )

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            raise ValueError(
                "Each benign dataset entry "
                "must be an object."
            )

        if "name" not in item:
            raise ValueError(
                "Benign dataset entry is "
                "missing name."
            )

        if "prompt" not in item:
            raise ValueError(
                "Benign dataset entry is "
                "missing prompt."
            )

    return data


def build_report(
    model_name,
    evaluator_name,
    defense_name,
    defense_threshold,
    attacks,
    baseline_results,
    defended_results,
    metrics,
    benign_results,
):
    return {
        "model": model_name,
        "evaluator": evaluator_name,
        "defense": defense_name,
        "defense_threshold": (
            defense_threshold
        ),
        "total_attacks": len(
            attacks
        ),
        "metrics": metrics,
        "benign_metrics": benign_results,
        "results": [
            {
                "attack": attack.name,
                "category": attack.category,
                "security_risk": (
                    get_security_risk_dict(
                        attack.category
                    )
                ),
                "baseline": asdict(
                    baseline
                ),
                "defended": asdict(
                    defended
                ),
            }
            for (
                attack,
                baseline,
                defended,
            ) in zip(
                attacks,
                baseline_results,
                defended_results,
            )
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


async def run_benchmark(
    attacks,
    runner,
    label,
):
    results = []

    print()
    print(
        label
    )
    print(
        "-" * 60
    )

    for index, attack in enumerate(
        attacks,
        start=1,
    ):
        print(
            f"[{index}/{len(attacks)}] "
            f"{attack.name}"
        )

        result = await runner.run(
            attack,
            attack.expected,
        )

        results.append(
            result
        )

        if result.blocked:
            status = "BLOCKED"

        elif result.successful:
            status = "SUCCESS"

        else:
            status = "FAILED"

        print(
            f"  Category : "
            f"{attack.category}"
        )

        print(
            f"  Status   : "
            f"{status}"
        )

        if result.blocked:
            print(
                f"  Reason   : "
                f"{result.defense_reason}"
            )

            print(
                f"  D.Score  : "
                f"{result.defense_score}"
            )

        else:
            print(
                f"  Score    : "
                f"{result.score}"
            )

            print(
                f"  Latency  : "
                f"{result.latency_ms:.2f} ms"
            )

    return results


async def main() -> None:
    args = parse_args()

    if args.threshold < 0:
        raise ValueError(
            "--threshold must be "
            "non-negative."
        )

    target = OllamaTarget(
        model=args.model
    )

    evaluator = build_evaluator(
        args.evaluator
    )

    defense = build_defense(
        args.defense,
        threshold=args.threshold,
    )

    attacks = load_attacks(
        args
    )

    baseline_runner = (
        DefenseBenchmarkRunner(
            target=target,
            evaluator=evaluator,
            defense=NoDefense(),
        )
    )

    defended_runner = (
        DefenseBenchmarkRunner(
            target=target,
            evaluator=evaluator,
            defense=defense,
        )
    )

    print()
    print(
        "AegisLLM Defense Benchmark"
    )
    print(
        "=" * 60
    )

    print(
        f"Target Model  : "
        f"{target.model_name}"
    )

    print(
        f"Evaluator     : "
        f"{args.evaluator}"
    )

    print(
        f"Defense       : "
        f"{defense.name}"
    )

    print(
        f"Threshold     : "
        f"{args.threshold}"
    )

    if args.all:
        print(
            "Attack Mode   : "
            "All categories"
        )

    else:
        print(
            f"Dataset       : "
            f"{args.dataset}"
        )

    print(
        f"Benign Dataset: "
        f"{args.benign_dataset}"
    )

    print(
        f"Total Attacks : "
        f"{len(attacks)}"
    )

    print(
        "=" * 60
    )

    baseline_results = (
        await run_benchmark(
            attacks=attacks,
            runner=baseline_runner,
            label=(
                "Baseline Run "
                "(No Defense)"
            ),
        )
    )

    defended_results = (
        await run_benchmark(
            attacks=attacks,
            runner=defended_runner,
            label=(
                f"Defended Run "
                f"({defense.name})"
            ),
        )
    )

    metrics = defense_metrics(
        baseline_results,
        defended_results,
    )

    benign_prompts = (
        load_benign_prompts(
            args.benign_dataset
        )
    )

    benign_results = benign_metrics(
        benign_prompts,
        defense,
    )

    print()
    print(
        "=" * 60
    )
    print(
        "Defense Benchmark Summary"
    )
    print(
        "=" * 60
    )

    print(
        f"Target Model       : "
        f"{target.model_name}"
    )

    print(
        f"Evaluator          : "
        f"{args.evaluator}"
    )

    print(
        f"Defense            : "
        f"{defense.name}"
    )

    print(
        f"Total Attacks      : "
        f"{metrics['total_attacks']}"
    )

    print(
        f"Baseline Successes : "
        f"{metrics['baseline_successes']}"
    )

    print(
        f"Defended Successes : "
        f"{metrics['defended_successes']}"
    )

    print(
        f"Blocked Attacks    : "
        f"{metrics['blocked_attacks']}"
    )

    print(
        f"Bypassed Attacks   : "
        f"{metrics['bypassed_attacks']}"
    )

    print(
        f"Baseline ASR       : "
        f"{metrics['baseline_asr']:.2%}"
    )

    print(
        f"Defended ASR       : "
        f"{metrics['defended_asr']:.2%}"
    )

    print(
        f"ASR Reduction      : "
        f"{metrics['asr_reduction']:+.2%}"
    )

    print(
        f"Block Rate         : "
        f"{metrics['block_rate']:.2%}"
    )

    print(
        f"Bypass Rate        : "
        f"{metrics['bypass_rate']:.2%}"
    )

    print()
    print(
        "Category Defense Results"
    )
    print(
        "-" * 60
    )

    print(
        f"{'Category':<20}"
        f"{'Baseline':>11}"
        f"{'Defended':>11}"
        f"{'Reduction':>12}"
        f"{'Blocked':>10}"
    )

    print(
        "-" * 64
    )

    for category, data in (
        metrics[
            "category_metrics"
        ].items()
    ):
        print(
            f"{category:<20}"
            f"{data['baseline_asr']:>10.2%}"
            f"{data['defended_asr']:>11.2%}"
            f"{data['asr_reduction']:>+12.2%}"
            f"{data['block_rate']:>10.2%}"
        )

    print()
    print(
        "Benign Control Results"
    )
    print(
        "-" * 60
    )

    print(
        f"Total Benign Prompts       : "
        f"{benign_results['total_prompts']}"
    )

    print(
        f"Allowed Benign Prompts     : "
        f"{benign_results['allowed_prompts']}"
    )

    print(
        f"Blocked Benign Prompts     : "
        f"{benign_results['blocked_prompts']}"
    )

    print(
        f"False Positive Rate        : "
        f"{benign_results['false_positive_rate']:.2%}"
    )

    print(
        f"Utility Preservation Rate  : "
        f"{benign_results['utility_preservation_rate']:.2%}"
    )

    print(
        "=" * 64
    )

    if args.output:
        report = build_report(
            model_name=target.model_name,
            evaluator_name=args.evaluator,
            defense_name=defense.name,
            defense_threshold=(
                args.threshold
            ),
            attacks=attacks,
            baseline_results=(
                baseline_results
            ),
            defended_results=(
                defended_results
            ),
            metrics=metrics,
            benign_results=(
                benign_results
            ),
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