import json
from pathlib import Path
from typing import Any


def build_report(
    model_name: str,
    attacks: list[Any],
    results: list[Any],
    success_rate: float,
) -> dict[str, Any]:
    return {
        "model": model_name,
        "total_attacks": len(results),
        "successful_attacks": sum(
            result.successful for result in results
        ),
        "attack_success_rate": success_rate,
        "results": [
            {
                "attack": attack.name,
                "category": attack.category,
                "successful": result.successful,
                "score": result.score,
                "latency_ms": result.latency_ms,
                "response": result.response,
            }
            for attack, result in zip(attacks, results)
        ],
    }


def save_report(report: dict[str, Any], output: str) -> None:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)