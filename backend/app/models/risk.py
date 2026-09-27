from typing import Dict

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float
    explanation: str


class RiskReport(BaseModel):
    total_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str
    factors: Dict[str, RiskFactor] = Field(
        default_factory=dict
    )