class ExactMatchEvaluator:
    """Checks whether an expected marker occurs in the model response."""

    def evaluate(
        self,
        response: str,
        expected_marker: str,
    ) -> tuple[bool, float]:

        successful = expected_marker.lower() in response.lower()
        score = 1.0 if successful else 0.0

        return successful, score