class ExactMatchEvaluator:
    """
    Checks whether the model response exactly matches
    the expected marker.

    Leading and trailing whitespace is ignored.
    Matching is case-sensitive.
    """

    def evaluate(
        self,
        response: str,
        expected_marker: str,
    ) -> tuple[bool, float]:
        if not expected_marker:
            return False, 0.0

        successful = response.strip() == expected_marker.strip()
        score = 1.0 if successful else 0.0

        return successful, score