from aegis.defenses.base import (
    Defense,
    DefenseDecision,
)
from aegis.defenses.benign import (
    benign_metrics,
)
from aegis.defenses.rule_guard import (
    RuleBasedDefense,
)


class BlockEverythingDefense(Defense):
    @property
    def name(self):
        return "block_everything"

    def inspect(self, prompt):
        return DefenseDecision(
            allowed=False,
            reason="Blocked.",
            score=1.0,
        )


def test_empty_benign_dataset():
    metrics = benign_metrics(
        [],
        RuleBasedDefense(),
    )

    assert metrics[
        "total_prompts"
    ] == 0

    assert metrics[
        "false_positive_rate"
    ] == 0.0

    assert metrics[
        "utility_preservation_rate"
    ] == 0.0


def test_safe_prompts_allowed():
    prompts = [
        {
            "name": "binary_search",
            "prompt": (
                "Explain how binary search works."
            ),
        },
        {
            "name": "dns",
            "prompt": (
                "What is the purpose of DNS?"
            ),
        },
    ]

    metrics = benign_metrics(
        prompts,
        RuleBasedDefense(),
    )

    assert metrics[
        "total_prompts"
    ] == 2

    assert metrics[
        "blocked_prompts"
    ] == 0

    assert metrics[
        "allowed_prompts"
    ] == 2

    assert metrics[
        "false_positive_rate"
    ] == 0.0

    assert metrics[
        "utility_preservation_rate"
    ] == 1.0


def test_block_everything_has_full_false_positive_rate():
    prompts = [
        {
            "name": "safe",
            "prompt": "Explain binary search.",
        }
    ]

    metrics = benign_metrics(
        prompts,
        BlockEverythingDefense(),
    )

    assert metrics[
        "blocked_prompts"
    ] == 1

    assert metrics[
        "false_positive_rate"
    ] == 1.0

    assert metrics[
        "utility_preservation_rate"
    ] == 0.0


def test_benign_results_preserved():
    prompts = [
        {
            "name": "safe",
            "prompt": "Explain binary search.",
        }
    ]

    metrics = benign_metrics(
        prompts,
        RuleBasedDefense(),
    )

    result = metrics["results"][0]

    assert result["name"] == "safe"
    assert result["blocked"] is False
    assert "reason" in result
    assert "score" in result