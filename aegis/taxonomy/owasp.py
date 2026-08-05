from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityRisk:
    """
    Represents a security risk classification.
    """

    taxonomy: str
    risk_id: str
    name: str
    description: str = ""


OWASP_LLM_PROMPT_INJECTION = SecurityRisk(
    taxonomy="OWASP LLM Top 10",
    risk_id="LLM01",
    name="Prompt Injection",
    description=(
        "Manipulation of an LLM through crafted "
        "inputs that influence its intended behavior."
    ),
)


CATEGORY_RISK_MAPPING = {
    "prompt_injection": (
        OWASP_LLM_PROMPT_INJECTION
    ),
    "jailbreak": (
        OWASP_LLM_PROMPT_INJECTION
    ),
    "encoding": (
        OWASP_LLM_PROMPT_INJECTION
    ),
}


def get_security_risk(
    category: str,
) -> SecurityRisk | None:
    """
    Return the security risk associated with an
    AegisLLM attack category.

    Unknown categories return None so custom attack
    categories can still be used without requiring
    an OWASP mapping.
    """

    return CATEGORY_RISK_MAPPING.get(
        category
    )


def get_security_risk_dict(
    category: str,
) -> dict[str, str] | None:
    """
    Return a JSON-serializable security risk mapping.
    """

    risk = get_security_risk(
        category
    )

    if risk is None:
        return None

    return {
        "taxonomy": risk.taxonomy,
        "risk_id": risk.risk_id,
        "name": risk.name,
        "description": risk.description,
    }