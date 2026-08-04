import json
import sys

import pytest

import scripts.run_defense_benchmark as cli
from aegis.defenses.base import NoDefense
from aegis.defenses.rule_guard import RuleBasedDefense
from aegis.defenses.runner import DefenseBenchmarkResult


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_defense_benchmark.py"],
    )

    args = cli.parse_args()

    assert args.model == "llama3.2:3b"
    assert (
        args.dataset
        == "datasets/attacks/prompt_injection.json"
    )
    assert args.all is False
    assert args.evaluator == "exact"
    assert args.defense == "rule_guard"
    assert args.threshold == 1.0

    assert (
        args.benign_dataset
        == "datasets/benign/prompts.json"
    )

    assert args.output is None


def test_parse_args_custom_values(
    monkeypatch,
):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_defense_benchmark.py",
            "--model",
            "test-model",
            "--all",
            "--evaluator",
            "contains",
            "--defense",
            "rule_guard",
            "--threshold",
            "2.0",
            "--benign-dataset",
            "custom-benign.json",
            "--output",
            "results/test.json",
        ],
    )

    args = cli.parse_args()

    assert args.model == "test-model"
    assert args.all is True
    assert args.evaluator == "contains"
    assert args.defense == "rule_guard"
    assert args.threshold == 2.0

    assert (
        args.benign_dataset
        == "custom-benign.json"
    )

    assert (
        args.output
        == "results/test.json"
    )


def test_build_exact_evaluator():
    evaluator = cli.build_evaluator(
        "exact"
    )

    assert (
        evaluator.__class__.__name__
        == "ExactMatchEvaluator"
    )


def test_build_contains_evaluator():
    evaluator = cli.build_evaluator(
        "contains"
    )

    assert (
        evaluator.__class__.__name__
        == "ContainsMatchEvaluator"
    )


def test_invalid_evaluator():
    with pytest.raises(
        ValueError,
        match="Unsupported evaluator",
    ):
        cli.build_evaluator(
            "invalid"
        )


def test_build_rule_guard():
    defense = cli.build_defense(
        "rule_guard",
        threshold=2.0,
    )

    assert isinstance(
        defense,
        RuleBasedDefense,
    )

    assert defense.name == "rule_guard"
    assert defense.threshold == 2.0


def test_build_no_defense():
    defense = cli.build_defense(
        "none"
    )

    assert isinstance(
        defense,
        NoDefense,
    )

    assert defense.name == "none"


def test_invalid_defense():
    with pytest.raises(
        ValueError,
        match="Unsupported defense",
    ):
        cli.build_defense(
            "invalid"
        )


def test_build_attacks():
    attacks = cli.build_attacks(
        "datasets/attacks/"
        "prompt_injection.json"
    )

    assert len(attacks) == 5

    for attack in attacks:
        assert (
            attack.category
            == "prompt_injection"
        )

        assert attack.name
        assert attack.prompt
        assert attack.expected


def test_load_benign_prompts():
    prompts = cli.load_benign_prompts(
        "datasets/benign/prompts.json"
    )

    assert len(prompts) == 10

    for item in prompts:
        assert "name" in item
        assert "prompt" in item


def test_load_benign_prompts_rejects_non_list(
    tmp_path,
):
    dataset = (
        tmp_path
        / "benign.json"
    )

    with dataset.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "name": "invalid",
                "prompt": "test",
            },
            file,
        )

    with pytest.raises(
        ValueError,
        match=(
            "Benign dataset must "
            "contain a JSON list"
        ),
    ):
        cli.load_benign_prompts(
            str(dataset)
        )


def test_load_benign_prompts_requires_name(
    tmp_path,
):
    dataset = (
        tmp_path
        / "benign.json"
    )

    with dataset.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [
                {
                    "prompt": "Safe prompt"
                }
            ],
            file,
        )

    with pytest.raises(
        ValueError,
        match="missing name",
    ):
        cli.load_benign_prompts(
            str(dataset)
        )


def test_load_benign_prompts_requires_prompt(
    tmp_path,
):
    dataset = (
        tmp_path
        / "benign.json"
    )

    with dataset.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [
                {
                    "name": "safe"
                }
            ],
            file,
        )

    with pytest.raises(
        ValueError,
        match="missing prompt",
    ):
        cli.load_benign_prompts(
            str(dataset)
        )


def make_result(
    *,
    defense,
    blocked,
    successful,
):
    return DefenseBenchmarkResult(
        attack="test_attack",
        category="prompt_injection",
        defense=defense,
        blocked=blocked,
        defense_reason="test",
        defense_score=(
            1.0
            if blocked
            else 0.0
        ),
        successful=successful,
        score=(
            1.0
            if successful
            else 0.0
        ),
        response=(
            "SUCCESS"
            if successful
            else ""
        ),
        latency_ms=10.0,
    )


def test_build_report():
    attack = type(
        "Attack",
        (),
        {
            "name": "test_attack",
            "category": (
                "prompt_injection"
            ),
        },
    )()

    baseline = make_result(
        defense="none",
        blocked=False,
        successful=True,
    )

    defended = make_result(
        defense="rule_guard",
        blocked=True,
        successful=False,
    )

    metrics = {
        "total_attacks": 1,
        "baseline_successes": 1,
        "defended_successes": 0,
        "blocked_attacks": 1,
        "bypassed_attacks": 0,
        "baseline_asr": 1.0,
        "defended_asr": 0.0,
        "asr_reduction": 1.0,
        "block_rate": 1.0,
        "bypass_rate": 0.0,
        "category_metrics": {},
    }

    benign_results = {
        "total_prompts": 1,
        "allowed_prompts": 1,
        "blocked_prompts": 0,
        "false_positive_rate": 0.0,
        "utility_preservation_rate": 1.0,
        "results": [],
    }

    report = cli.build_report(
        model_name="test-model",
        evaluator_name="exact",
        defense_name="rule_guard",
        defense_threshold=1.0,
        attacks=[attack],
        baseline_results=[baseline],
        defended_results=[defended],
        metrics=metrics,
        benign_results=benign_results,
    )

    assert report["model"] == "test-model"

    assert (
        report["evaluator"]
        == "exact"
    )

    assert (
        report["defense"]
        == "rule_guard"
    )

    assert (
        report["defense_threshold"]
        == 1.0
    )

    assert (
        report["total_attacks"]
        == 1
    )

    assert (
        report["metrics"][
            "asr_reduction"
        ]
        == 1.0
    )

    assert (
        report["benign_metrics"][
            "false_positive_rate"
        ]
        == 0.0
    )

    assert len(
        report["results"]
    ) == 1

    assert (
        report["results"][0][
            "baseline"
        ]["successful"]
        is True
    )

    assert (
        report["results"][0][
            "defended"
        ]["blocked"]
        is True
    )


def test_save_report(
    tmp_path,
):
    report = {
        "model": "test-model",
        "defense": "rule_guard",
        "metrics": {
            "asr_reduction": 0.5,
        },
        "benign_metrics": {
            "false_positive_rate": 0.0,
        },
    }

    output = (
        tmp_path
        / "reports"
        / "defense.json"
    )

    cli.save_report(
        report,
        str(output),
    )

    assert output.exists()

    with output.open(
        "r",
        encoding="utf-8",
    ) as file:
        loaded = json.load(
            file
        )

    assert loaded == report