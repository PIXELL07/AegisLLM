from typing import Any


def adaptive_metrics(
    results: list[Any],
) -> dict[str, Any]:
    """
    Calculate aggregate metrics for adaptive attack results.
    """

    total_attacks = len(results)

    if total_attacks == 0:
        return {
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

    original_successes = 0
    adaptive_successes = 0
    total_attempts = 0

    successful_attempt_counts: list[int] = []
    strategy_successes: dict[str, int] = {}

    category_data: dict[str, dict[str, int]] = {}

    for result in results:
        total_attempts += result.attempts_used

        category = result.category

        if category not in category_data:
            category_data[category] = {
                "total_attacks": 0,
                "original_successes": 0,
                "adaptive_successes": 0,
            }

        category_data[
            category
        ]["total_attacks"] += 1

        if result.successful:
            adaptive_successes += 1

            category_data[
                category
            ]["adaptive_successes"] += 1

            successful_attempt_counts.append(
                result.attempts_used
            )

            if result.successful_attempt == 1:
                original_successes += 1

                category_data[
                    category
                ]["original_successes"] += 1

            strategy = result.successful_strategy

            if strategy is not None:
                strategy_successes[strategy] = (
                    strategy_successes.get(
                        strategy,
                        0,
                    )
                    + 1
                )

    original_asr = (
        original_successes
        / total_attacks
    )

    adaptive_asr = (
        adaptive_successes
        / total_attacks
    )

    adaptive_gain = (
        adaptive_asr
        - original_asr
    )

    average_attempts = (
        total_attempts
        / total_attacks
    )

    if successful_attempt_counts:
        average_attempts_to_success = (
            sum(successful_attempt_counts)
            / len(successful_attempt_counts)
        )
    else:
        average_attempts_to_success = 0.0

    categories: dict[str, dict[str, Any]] = {}

    for category, data in category_data.items():
        total = data["total_attacks"]

        category_original_asr = (
            data["original_successes"]
            / total
        )

        category_adaptive_asr = (
            data["adaptive_successes"]
            / total
        )

        categories[category] = {
            "total_attacks": total,
            "original_successes": (
                data["original_successes"]
            ),
            "adaptive_successes": (
                data["adaptive_successes"]
            ),
            "original_asr": (
                category_original_asr
            ),
            "adaptive_asr": (
                category_adaptive_asr
            ),
            "adaptive_gain": (
                category_adaptive_asr
                - category_original_asr
            ),
        }

    return {
        "total_attacks": total_attacks,
        "original_successes": original_successes,
        "adaptive_successes": adaptive_successes,
        "original_asr": original_asr,
        "adaptive_asr": adaptive_asr,
        "adaptive_gain": adaptive_gain,
        "average_attempts": average_attempts,
        "average_attempts_to_success": (
            average_attempts_to_success
        ),
        "strategy_successes": strategy_successes,
        "category_metrics": categories,
    }