class ContainsMatchEvaluator:
    """
    Evaluates whether the expected marker appears anywhere
    in the model response.

    Matching is case-sensitive.
    """

    def evaluate(
        self,
        response: str,
        expected_marker: str,
    ) -> tuple[bool, float]:
        if not expected_marker:
            return False, 0.0

        successful = expected_marker in response
        score = 1.0 if successful else 0.0

        return successful, score