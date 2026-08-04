from types import SimpleNamespace

import pytest

from aegis.defenses.metrics import (
    defense_metrics,
)


def result(
    *,
    category,
    successful,
    blocked=False,
):
    return SimpleNamespace(
        category=category,
        successful=successful,
        blocked=blocked,
    )


def test_empty_results():
    metrics = defense_metrics(
        [],
        [],
    )

    assert metrics == {
        "total_attacks": 0,
        "baseline_successes": 0,
        "defended_successes": 0,
        "blocked_attacks": 0,
        "bypassed_attacks": 0,
        "baseline_asr": 0.0,
        "defended_asr": 0.0,
        "asr_reduction": 0.0,
        "block_rate": 0.0,
        "bypass_rate": 0.0,
        "category_metrics": {},
    }


def test_result_lengths_must_match():
    with pytest.raises(
        ValueError,
        match="same number of attacks",
    ):
        defense_metrics(
            [
                result(
                    category="prompt_injection",
                    successful=True,
                )
            ],
            [],
        )


def test_basic_defense_metrics():
    baseline = [
        result(
            category="prompt_injection",
            successful=True,
        ),
        result(
            category="prompt_injection",
            successful=True,
        ),
        result(
            category="prompt_injection",
            successful=False,
        ),
        result(
            category="prompt_injection",
            successful=False,
        ),
    ]

    defended = [
        result(
            category="prompt_injection",
            successful=False,
            blocked=True,
        ),
        result(
            category="prompt_injection",
            successful=True,
            blocked=False,
        ),
        result(
            category="prompt_injection",
            successful=False,
            blocked=False,
        ),
        result(
            category="prompt_injection",
            successful=False,
            blocked=True,
        ),
    ]

    metrics = defense_metrics(
        baseline,
        defended,
    )

    assert metrics[
        "total_attacks"
    ] == 4

    assert metrics[
        "baseline_successes"
    ] == 2

    assert metrics[
        "defended_successes"
    ] == 1

    assert metrics[
        "blocked_attacks"
    ] == 2

    assert metrics[
        "bypassed_attacks"
    ] == 1

    assert metrics[
        "baseline_asr"
    ] == 0.5

    assert metrics[
        "defended_asr"
    ] == 0.25

    assert metrics[
        "asr_reduction"
    ] == 0.25

    assert metrics[
        "block_rate"
    ] == 0.5

    assert metrics[
        "bypass_rate"
    ] == 0.25


def test_complete_mitigation():
    baseline = [
        result(
            category="jailbreak",
            successful=True,
        ),
        result(
            category="jailbreak",
            successful=True,
        ),
    ]

    defended = [
        result(
            category="jailbreak",
            successful=False,
            blocked=True,
        ),
        result(
            category="jailbreak",
            successful=False,
            blocked=True,
        ),
    ]

    metrics = defense_metrics(
        baseline,
        defended,
    )

    assert metrics[
        "baseline_asr"
    ] == 1.0

    assert metrics[
        "defended_asr"
    ] == 0.0

    assert metrics[
        "asr_reduction"
    ] == 1.0

    assert metrics[
        "block_rate"
    ] == 1.0

    assert metrics[
        "bypass_rate"
    ] == 0.0


def test_defense_with_no_effect():
    baseline = [
        result(
            category="jailbreak",
            successful=True,
        )
    ]

    defended = [
        result(
            category="jailbreak",
            successful=True,
            blocked=False,
        )
    ]

    metrics = defense_metrics(
        baseline,
        defended,
    )

    assert metrics[
        "baseline_asr"
    ] == 1.0

    assert metrics[
        "defended_asr"
    ] == 1.0

    assert metrics[
        "asr_reduction"
    ] == 0.0

    assert metrics[
        "block_rate"
    ] == 0.0

    assert metrics[
        "bypass_rate"
    ] == 1.0


def test_category_metrics():
    baseline = [
        result(
            category="prompt_injection",
            successful=True,
        ),
        result(
            category="prompt_injection",
            successful=False,
        ),
        result(
            category="jailbreak",
            successful=True,
        ),
        result(
            category="jailbreak",
            successful=True,
        ),
    ]

    defended = [
        result(
            category="prompt_injection",
            successful=False,
            blocked=True,
        ),
        result(
            category="prompt_injection",
            successful=False,
            blocked=False,
        ),
        result(
            category="jailbreak",
            successful=True,
            blocked=False,
        ),
        result(
            category="jailbreak",
            successful=False,
            blocked=True,
        ),
    ]

    metrics = defense_metrics(
        baseline,
        defended,
    )

    prompt_injection = metrics[
        "category_metrics"
    ]["prompt_injection"]

    assert prompt_injection[
        "baseline_asr"
    ] == 0.5

    assert prompt_injection[
        "defended_asr"
    ] == 0.0

    assert prompt_injection[
        "asr_reduction"
    ] == 0.5

    assert prompt_injection[
        "block_rate"
    ] == 0.5

    jailbreak = metrics[
        "category_metrics"
    ]["jailbreak"]

    assert jailbreak[
        "baseline_asr"
    ] == 1.0

    assert jailbreak[
        "defended_asr"
    ] == 0.5

    assert jailbreak[
        "asr_reduction"
    ] == 0.5

    assert jailbreak[
        "block_rate"
    ] == 0.5


def test_category_mismatch_rejected():
    baseline = [
        result(
            category="prompt_injection",
            successful=True,
        )
    ]

    defended = [
        result(
            category="jailbreak",
            successful=False,
            blocked=True,
        )
    ]

    with pytest.raises(
        ValueError,
        match="categories must match",
    ):
        defense_metrics(
            baseline,
            defended,
        )