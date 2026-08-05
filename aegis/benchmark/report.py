import json
from pathlib import Path
from typing import Any
from aegis.metadata.run import create_run_metadata

from aegis.taxonomy.owasp import (
    get_security_risk_dict,
)


def build_report(
    model_name: str,
    attacks: list[Any],
    results: list[Any],
    success_rate: float,
    evaluator_name: str = "exact",
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_metadata = create_run_metadata(
        benchmark_type="standard",
        model=model_name,
        evaluator=evaluator_name,
        configuration=configuration or {
            "total_attacks": len(attacks),
        },
    )

    return {
        "model": model_name,
        "run_metadata": run_metadata,
        "total_attacks": len(results),
        "successful_attacks": sum(
            result.successful
            for result in results
        ),
        "attack_success_rate": success_rate,
        "results": [
            {
                "attack": attack.name,
                "category": attack.category,
                "security_risk": (
                    get_security_risk_dict(
                        attack.category
                    )
                ),
                "successful": result.successful,
                "score": result.score,
                "latency_ms": result.latency_ms,
                "response": result.response,
            }
            for attack, result in zip(
                attacks,
                results,
            )
        ],
    }


def save_report(
    report: dict[str, Any],
    output: str,
) -> None:
    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )