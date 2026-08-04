from typing import Any

from aegis.defenses.base import Defense


def benign_metrics(
    prompts: list[dict[str, Any]],
    defense: Defense,
) -> dict[str, Any]:
    """
    Measure how often a defense incorrectly blocks
    benign prompts.
    """

    total_prompts = len(prompts)

    if total_prompts == 0:
        return {
            "total_prompts": 0,
            "allowed_prompts": 0,
            "blocked_prompts": 0,
            "false_positive_rate": 0.0,
            "utility_preservation_rate": 0.0,
            "results": [],
        }

    results = []
    blocked_prompts = 0

    for item in prompts:
        decision = defense.inspect(
            item["prompt"]
        )

        blocked = not decision.allowed

        if blocked:
            blocked_prompts += 1

        results.append(
            {
                "name": item["name"],
                "prompt": item["prompt"],
                "blocked": blocked,
                "reason": decision.reason,
                "score": decision.score,
            }
        )

    allowed_prompts = (
        total_prompts
        - blocked_prompts
    )

    false_positive_rate = (
        blocked_prompts
        / total_prompts
    )

    utility_preservation_rate = (
        allowed_prompts
        / total_prompts
    )

    return {
        "total_prompts": total_prompts,
        "allowed_prompts": allowed_prompts,
        "blocked_prompts": blocked_prompts,
        "false_positive_rate": (
            false_positive_rate
        ),
        "utility_preservation_rate": (
            utility_preservation_rate
        ),
        "results": results,
    }