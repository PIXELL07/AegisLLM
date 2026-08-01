from pydantic import BaseModel, Field


class AttackResult(BaseModel):
    """Result produced by a single adversarial benchmark execution."""

    attack_name: str
    attack_category: str
    prompt: str
    response: str
    successful: bool

    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Attack success score between 0 and 1.",
    )

    latency_ms: float
    target_model: str