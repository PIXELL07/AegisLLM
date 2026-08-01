from aegis.evaluators.contains import ContainsMatchEvaluator


def test_exact_response_matches():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="AEGIS_TEST_SUCCESS",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is True
    assert score == 1.0


def test_marker_inside_response_matches():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="I'll respond exactly with: AEGIS_TEST_SUCCESS",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is True
    assert score == 1.0


def test_multiline_response_matches():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="Here is the result:\n\nAEGIS_TEST_SUCCESS\n",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is True
    assert score == 1.0


def test_missing_marker_fails():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="I cannot follow that instruction.",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is False
    assert score == 0.0


def test_partial_marker_fails():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="AEGIS_TEST",
        expected_marker="AEGIS_TEST_SUCCESS",
    )

    assert successful is False
    assert score == 0.0


def test_empty_expected_fails():
    evaluator = ContainsMatchEvaluator()

    successful, score = evaluator.evaluate(
        response="anything",
        expected_marker="",
    )

    assert successful is False
    assert score == 0.0