from datetime import datetime
from uuid import UUID

import pytest

from aegis.metadata.run import (
    create_run_metadata,
)


def test_create_run_metadata():
    metadata = create_run_metadata(
        benchmark_type="standard",
        model="llama3.2:3b",
        evaluator="exact",
    )

    assert (
        metadata["benchmark_type"]
        == "standard"
    )

    assert (
        metadata["model"]
        == "llama3.2:3b"
    )

    assert (
        metadata["evaluator"]
        == "exact"
    )

    assert metadata["configuration"] == {}


def test_run_id_is_valid_uuid():
    metadata = create_run_metadata(
        benchmark_type="standard",
        model="test-model",
        evaluator="exact",
    )

    run_id = UUID(
        metadata["run_id"]
    )

    assert str(run_id) == metadata["run_id"]


def test_run_ids_are_unique():
    first = create_run_metadata(
        benchmark_type="standard",
        model="test-model",
        evaluator="exact",
    )

    second = create_run_metadata(
        benchmark_type="standard",
        model="test-model",
        evaluator="exact",
    )

    assert (
        first["run_id"]
        != second["run_id"]
    )


def test_timestamp_is_iso8601():
    metadata = create_run_metadata(
        benchmark_type="standard",
        model="test-model",
        evaluator="exact",
    )

    timestamp = datetime.fromisoformat(
        metadata["timestamp"]
    )

    assert timestamp.tzinfo is not None


def test_configuration_preserved():
    configuration = {
        "dataset": "prompt_injection",
        "all_categories": False,
    }

    metadata = create_run_metadata(
        benchmark_type="standard",
        model="test-model",
        evaluator="contains",
        configuration=configuration,
    )

    assert (
        metadata["configuration"]
        == configuration
    )


def test_configuration_is_copied():
    configuration = {
        "max_attempts": 5,
    }

    metadata = create_run_metadata(
        benchmark_type="adaptive",
        model="test-model",
        evaluator="exact",
        configuration=configuration,
    )

    configuration["max_attempts"] = 10

    assert (
        metadata["configuration"][
            "max_attempts"
        ]
        == 5
    )


@pytest.mark.parametrize(
    "field,value,error",
    [
        (
            "benchmark_type",
            "",
            "benchmark_type must not be empty",
        ),
        (
            "model",
            "",
            "model must not be empty",
        ),
        (
            "evaluator",
            "",
            "evaluator must not be empty",
        ),
    ],
)
def test_required_metadata_fields(
    field,
    value,
    error,
):
    arguments = {
        "benchmark_type": "standard",
        "model": "test-model",
        "evaluator": "exact",
    }

    arguments[field] = value

    with pytest.raises(
        ValueError,
        match=error,
    ):
        create_run_metadata(
            **arguments
        )