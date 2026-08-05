from aegis.taxonomy.owasp import (
    OWASP_LLM_PROMPT_INJECTION,
    SecurityRisk,
    get_security_risk,
    get_security_risk_dict,
)


def test_security_risk_model():
    risk = SecurityRisk(
        taxonomy="Test Taxonomy",
        risk_id="TEST01",
        name="Test Risk",
        description="Test description.",
    )

    assert risk.taxonomy == "Test Taxonomy"
    assert risk.risk_id == "TEST01"
    assert risk.name == "Test Risk"
    assert risk.description == "Test description."


def test_prompt_injection_mapping():
    risk = get_security_risk(
        "prompt_injection"
    )

    assert (
        risk
        == OWASP_LLM_PROMPT_INJECTION
    )

    assert risk.risk_id == "LLM01"
    assert risk.name == "Prompt Injection"


def test_jailbreak_mapping():
    risk = get_security_risk(
        "jailbreak"
    )

    assert risk is not None
    assert risk.risk_id == "LLM01"


def test_encoding_mapping():
    risk = get_security_risk(
        "encoding"
    )

    assert risk is not None
    assert risk.risk_id == "LLM01"


def test_unknown_category():
    risk = get_security_risk(
        "custom_attack"
    )

    assert risk is None


def test_security_risk_dict():
    risk = get_security_risk_dict(
        "prompt_injection"
    )

    assert risk is not None

    assert (
        risk["taxonomy"]
        == "OWASP LLM Top 10"
    )

    assert risk["risk_id"] == "LLM01"
    assert risk["name"] == "Prompt Injection"

    assert "description" in risk


def test_unknown_category_dict():
    risk = get_security_risk_dict(
        "unknown"
    )

    assert risk is None