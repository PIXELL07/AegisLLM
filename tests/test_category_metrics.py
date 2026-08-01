from types import SimpleNamespace

from aegis.benchmark.metrics import category_metrics


def test_category_metrics():
    results = [
        SimpleNamespace(
            category="prompt_injection",
            successful=True,
        ),
        SimpleNamespace(
            category="prompt_injection",
            successful=False,
        ),
        SimpleNamespace(
            category="prompt_injection",
            successful=True,
        ),
        SimpleNamespace(
            category="jailbreak",
            successful=True,
        ),
        SimpleNamespace(
            category="jailbreak",
            successful=False,
        ),
    ]

    metrics = category_metrics(results)

    assert metrics["prompt_injection"]["total_attacks"] == 3
    assert metrics["prompt_injection"]["successful_attacks"] == 2
    assert metrics["prompt_injection"]["attack_success_rate"] == 2 / 3

    assert metrics["jailbreak"]["total_attacks"] == 2
    assert metrics["jailbreak"]["successful_attacks"] == 1
    assert metrics["jailbreak"]["attack_success_rate"] == 0.5


def test_category_metrics_empty():
    assert category_metrics([]) == {}


def test_category_metrics_all_successful():
    results = [
        SimpleNamespace(
            category="prompt_injection",
            successful=True,
        ),
        SimpleNamespace(
            category="prompt_injection",
            successful=True,
        ),
    ]

    metrics = category_metrics(results)

    assert metrics["prompt_injection"]["total_attacks"] == 2
    assert metrics["prompt_injection"]["successful_attacks"] == 2
    assert metrics["prompt_injection"]["attack_success_rate"] == 1.0