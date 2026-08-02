import pytest

from aegis.adaptive.metrics import (
    adaptive_metrics,
)
from aegis.adaptive.runner import (
    AdaptiveAttackResult,
)


def make_result(
    *,
    successful,
    attempts_used,
    successful_attempt=None,
    successful_strategy=None,
):
    return AdaptiveAttackResult(
        attack="test_attack",
        category="prompt_injection",
        successful=successful,
        attempts_used=attempts_used,
        successful_attempt=successful_attempt,
        successful_strategy=successful_strategy,
        final_score=(
            1.0
            if successful
            else 0.0
        ),
        final_response=(
            "SUCCESS"
            if successful
            else "REFUSED"
        ),
        attempt_history=[],
    )


def test_empty_results():
    metrics = adaptive_metrics([])

    assert metrics == {
        "total_attacks": 0,
        "original_successes": 0,
        "adaptive_successes": 0,
        "original_asr": 0.0,
        "adaptive_asr": 0.0,
        "adaptive_gain": 0.0,
        "average_attempts": 0.0,
        "average_attempts_to_success": 0.0,
        "strategy_successes": {},
        "category_metrics": {},
    }

def test_original_success():
    results = [
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        )
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "original_successes"
    ] == 1

    assert metrics[
        "adaptive_successes"
    ] == 1

    assert metrics[
        "original_asr"
    ] == 1.0

    assert metrics[
        "adaptive_asr"
    ] == 1.0

    assert metrics[
        "adaptive_gain"
    ] == 0.0


def test_adaptive_mutation_increases_asr():
    results = [
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
        make_result(
            successful=True,
            attempts_used=2,
            successful_attempt=2,
            successful_strategy="roleplay",
        ),
        make_result(
            successful=False,
            attempts_used=5,
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "original_successes"
    ] == 1

    assert metrics[
        "adaptive_successes"
    ] == 2

    assert metrics[
        "original_asr"
    ] == pytest.approx(
        1 / 3
    )

    assert metrics[
        "adaptive_asr"
    ] == pytest.approx(
        2 / 3
    )

    assert metrics[
        "adaptive_gain"
    ] == pytest.approx(
        1 / 3
    )


def test_average_attempts():
    results = [
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
        make_result(
            successful=True,
            attempts_used=3,
            successful_attempt=3,
            successful_strategy="context_wrapping",
        ),
        make_result(
            successful=False,
            attempts_used=5,
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "average_attempts"
    ] == pytest.approx(
        3.0
    )


def test_average_attempts_to_success():
    results = [
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
        make_result(
            successful=True,
            attempts_used=3,
            successful_attempt=3,
            successful_strategy="context_wrapping",
        ),
        make_result(
            successful=False,
            attempts_used=5,
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "average_attempts_to_success"
    ] == pytest.approx(
        2.0
    )


def test_no_successful_attacks():
    results = [
        make_result(
            successful=False,
            attempts_used=5,
        ),
        make_result(
            successful=False,
            attempts_used=5,
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "original_asr"
    ] == 0.0

    assert metrics[
        "adaptive_asr"
    ] == 0.0

    assert metrics[
        "adaptive_gain"
    ] == 0.0

    assert metrics[
        "average_attempts_to_success"
    ] == 0.0


def test_strategy_success_counts():
    results = [
        make_result(
            successful=True,
            attempts_used=2,
            successful_attempt=2,
            successful_strategy="roleplay",
        ),
        make_result(
            successful=True,
            attempts_used=2,
            successful_attempt=2,
            successful_strategy="roleplay",
        ),
        make_result(
            successful=True,
            attempts_used=3,
            successful_attempt=3,
            successful_strategy="context_wrapping",
        ),
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "strategy_successes"
    ] == {
        "roleplay": 2,
        "context_wrapping": 1,
        "original": 1,
    }


def test_all_original_successes_have_no_gain():
    results = [
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
        make_result(
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
        ),
    ]

    metrics = adaptive_metrics(
        results
    )

    assert metrics[
        "original_asr"
    ] == 1.0

    assert metrics[
        "adaptive_asr"
    ] == 1.0

    assert metrics[
        "adaptive_gain"
    ] == 0.0

def test_category_adaptive_metrics():
    results = [
        AdaptiveAttackResult(
            attack="pi_1",
            category="prompt_injection",
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
            final_score=1.0,
            final_response="SUCCESS",
            attempt_history=[],
        ),
        AdaptiveAttackResult(
            attack="pi_2",
            category="prompt_injection",
            successful=True,
            attempts_used=2,
            successful_attempt=2,
            successful_strategy="roleplay",
            final_score=1.0,
            final_response="SUCCESS",
            attempt_history=[],
        ),
        AdaptiveAttackResult(
            attack="jb_1",
            category="jailbreak",
            successful=False,
            attempts_used=5,
            successful_attempt=None,
            successful_strategy=None,
            final_score=0.0,
            final_response="REFUSED",
            attempt_history=[],
        ),
    ]

    metrics = adaptive_metrics(results)

    prompt_injection = metrics[
        "category_metrics"
    ]["prompt_injection"]

    assert prompt_injection[
        "total_attacks"
    ] == 2

    assert prompt_injection[
        "original_successes"
    ] == 1

    assert prompt_injection[
        "adaptive_successes"
    ] == 2

    assert prompt_injection[
        "original_asr"
    ] == 0.5

    assert prompt_injection[
        "adaptive_asr"
    ] == 1.0

    assert prompt_injection[
        "adaptive_gain"
    ] == 0.5


def test_category_without_successes():
    results = [
        AdaptiveAttackResult(
            attack="encoding_1",
            category="encoding",
            successful=False,
            attempts_used=5,
            successful_attempt=None,
            successful_strategy=None,
            final_score=0.0,
            final_response="REFUSED",
            attempt_history=[],
        )
    ]

    metrics = adaptive_metrics(results)

    encoding = metrics[
        "category_metrics"
    ]["encoding"]

    assert encoding[
        "total_attacks"
    ] == 1

    assert encoding[
        "original_successes"
    ] == 0

    assert encoding[
        "adaptive_successes"
    ] == 0

    assert encoding[
        "original_asr"
    ] == 0.0

    assert encoding[
        "adaptive_asr"
    ] == 0.0

    assert encoding[
        "adaptive_gain"
    ] == 0.0


def test_multiple_category_gains():
    results = [
        AdaptiveAttackResult(
            attack="pi",
            category="prompt_injection",
            successful=True,
            attempts_used=2,
            successful_attempt=2,
            successful_strategy="roleplay",
            final_score=1.0,
            final_response="SUCCESS",
            attempt_history=[],
        ),
        AdaptiveAttackResult(
            attack="jb",
            category="jailbreak",
            successful=True,
            attempts_used=1,
            successful_attempt=1,
            successful_strategy="original",
            final_score=1.0,
            final_response="SUCCESS",
            attempt_history=[],
        ),
    ]

    metrics = adaptive_metrics(results)

    prompt_injection = metrics[
        "category_metrics"
    ]["prompt_injection"]

    jailbreak = metrics[
        "category_metrics"
    ]["jailbreak"]

    assert prompt_injection[
        "original_asr"
    ] == 0.0

    assert prompt_injection[
        "adaptive_asr"
    ] == 1.0

    assert prompt_injection[
        "adaptive_gain"
    ] == 1.0

    assert jailbreak[
        "original_asr"
    ] == 1.0

    assert jailbreak[
        "adaptive_asr"
    ] == 1.0

    assert jailbreak[
        "adaptive_gain"
    ] == 0.0