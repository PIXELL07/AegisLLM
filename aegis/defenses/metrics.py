from typing import Any


def defense_metrics(
    baseline_results: list[Any],
    defended_results: list[Any],
) -> dict[str, Any]:
    """
    Compare baseline attack results against defended results.

    Both result lists must represent the same attacks in
    the same order.
    """

    if len(baseline_results) != len(defended_results):
        raise ValueError(
            "Baseline and defended results must contain "
            "the same number of attacks."
        )

    total_attacks = len(defended_results)

    if total_attacks == 0:
        return {
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

    baseline_successes = 0
    defended_successes = 0
    blocked_attacks = 0
    bypassed_attacks = 0

    category_data: dict[
        str,
        dict[str, int],
    ] = {}

    for baseline, defended in zip(
        baseline_results,
        defended_results,
    ):
        baseline_category = getattr(
            baseline,
            "category",
            "unknown",
        )

        defended_category = getattr(
            defended,
            "category",
            "unknown",
        )

        if baseline_category != defended_category:
            raise ValueError(
                "Baseline and defended result categories "
                "must match."
            )

        category = defended_category

        if category not in category_data:
            category_data[category] = {
                "total_attacks": 0,
                "baseline_successes": 0,
                "defended_successes": 0,
                "blocked_attacks": 0,
                "bypassed_attacks": 0,
            }

        data = category_data[category]

        data["total_attacks"] += 1

        if baseline.successful:
            baseline_successes += 1
            data["baseline_successes"] += 1

        if defended.successful:
            defended_successes += 1
            data["defended_successes"] += 1

        if defended.blocked:
            blocked_attacks += 1
            data["blocked_attacks"] += 1

        if (
            not defended.blocked
            and defended.successful
        ):
            bypassed_attacks += 1
            data["bypassed_attacks"] += 1

    baseline_asr = (
        baseline_successes
        / total_attacks
    )

    defended_asr = (
        defended_successes
        / total_attacks
    )

    asr_reduction = (
        baseline_asr
        - defended_asr
    )

    block_rate = (
        blocked_attacks
        / total_attacks
    )

    bypass_rate = (
        bypassed_attacks
        / total_attacks
    )

    categories: dict[
        str,
        dict[str, Any],
    ] = {}

    for category, data in (
        category_data.items()
    ):
        total = data["total_attacks"]

        category_baseline_asr = (
            data["baseline_successes"]
            / total
        )

        category_defended_asr = (
            data["defended_successes"]
            / total
        )

        categories[category] = {
            "total_attacks": total,
            "baseline_successes": (
                data["baseline_successes"]
            ),
            "defended_successes": (
                data["defended_successes"]
            ),
            "blocked_attacks": (
                data["blocked_attacks"]
            ),
            "bypassed_attacks": (
                data["bypassed_attacks"]
            ),
            "baseline_asr": (
                category_baseline_asr
            ),
            "defended_asr": (
                category_defended_asr
            ),
            "asr_reduction": (
                category_baseline_asr
                - category_defended_asr
            ),
            "block_rate": (
                data["blocked_attacks"]
                / total
            ),
            "bypass_rate": (
                data["bypassed_attacks"]
                / total
            ),
        }

    return {
        "total_attacks": total_attacks,
        "baseline_successes": baseline_successes,
        "defended_successes": defended_successes,
        "blocked_attacks": blocked_attacks,
        "bypassed_attacks": bypassed_attacks,
        "baseline_asr": baseline_asr,
        "defended_asr": defended_asr,
        "asr_reduction": asr_reduction,
        "block_rate": block_rate,
        "bypass_rate": bypass_rate,
        "category_metrics": categories,
    }