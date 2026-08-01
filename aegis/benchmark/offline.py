from typing import Any


def evaluate_saved_results(
    results: list[dict[str, Any]],
    evaluator: Any,
) -> list[dict[str, Any]]:
    """
    Re-evaluate previously generated model responses.

    Each result must contain:
    - attack
    - category
    - expected
    - response

    The model is not called again.
    """

    evaluated_results = []

    for item in results:
        expected = item.get("expected")
        response = item.get("response", "")

        if expected is None:
            raise ValueError(
                f"Missing expected marker for attack: "
                f"{item.get('attack', 'unknown')}"
            )

        successful, score = evaluator.evaluate(
            response=response,
            expected_marker=expected,
        )

        evaluated_results.append(
            {
                **item,
                "successful": successful,
                "score": score,
            }
        )

    return evaluated_results