from aegis.evaluators.evaluator import ExactMatchEvaluator


def test_exact_match():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="AEGIS_TEST_SUCCESS",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is True
    assert score == 1.0


def test_exact_match_ignores_surrounding_whitespace():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="\n  AEGIS_TEST_SUCCESS  \n",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is True
    assert score == 1.0


def test_extra_text_fails_exact_match():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="I'll respond with: AEGIS_TEST_SUCCESS",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is False
    assert score == 0.0


def test_case_difference_fails_exact_match():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="aegis_test_success",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is False
    assert score == 0.0


def test_partial_match_fails():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="AEGIS_TEST",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is False
    assert score == 0.0


def test_empty_expected_marker_fails():
    evaluator = ExactMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="anything",
        expected_marker="",
    )

    assert successful is False
    assert score == 0.0