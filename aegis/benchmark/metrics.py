from aegis.schemas.result import AttackResult


def attack_success_rate(results: list[AttackResult]) -> float:
    """Calculate the proportion of attacks that successfully bypassed the target."""

    if not results:
        return 0.0

    successful_attacks = sum(
        result.successful for result in results
    )

    return successful_attacks / len(results)