from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def create_run_metadata(
    *,
    benchmark_type: str,
    model: str,
    evaluator: str,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create metadata describing a single AegisLLM
    benchmark execution.

    The metadata is JSON serializable and can be
    embedded directly inside benchmark reports.
    """

    if not benchmark_type:
        raise ValueError(
            "benchmark_type must not be empty."
        )

    if not model:
        raise ValueError(
            "model must not be empty."
        )

    if not evaluator:
        raise ValueError(
            "evaluator must not be empty."
        )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "run_id": str(uuid4()),
        "timestamp": timestamp,
        "benchmark_type": benchmark_type,
        "model": model,
        "evaluator": evaluator,
        "configuration": (
            dict(configuration)
            if configuration
            else {}
        ),
    }