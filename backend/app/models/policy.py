from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PolicyOperator(str, Enum):
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    CONTAINS = "CONTAINS"


class PolicyDecisionTarget(str, Enum):
    ALLOW = "ALLOW"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    BLOCK = "BLOCK"


class PolicyRule(BaseModel):
    rule_id: str
    description: str
    action: str
    field: str
    operator: PolicyOperator
    value: Any
    severity: int = Field(..., ge=1, le=10)
    target_decision: PolicyDecisionTarget


class TriggeredPolicy(BaseModel):
    rule_id: str
    field: str
    actual_value: Any
    expected_value: Any
    operator: PolicyOperator
    severity: int
    target_decision: PolicyDecisionTarget
    explanation: str


class PolicyResult(BaseModel):
    passed: bool
    triggered_rules: List[TriggeredPolicy] = Field(
        default_factory=list
    )
    recommended_decision: Optional[PolicyDecisionTarget] = None