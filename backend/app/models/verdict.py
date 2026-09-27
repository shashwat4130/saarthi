from enum import Enum

from pydantic import BaseModel

from app.models.policy import PolicyResult
from app.models.risk import RiskReport
from app.models.verification import VerificationReport


class DecisionEnum(str, Enum):
    ALLOW = "ALLOW"
    RETRY = "RETRY"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    BLOCK = "BLOCK"


class GovernanceVerdict(BaseModel):
    action_id: str
    agent_id: str
    action: str
    decision: DecisionEnum
    reason: str
    verification: VerificationReport
    policy: PolicyResult
    risk: RiskReport
    audit_event_id: str
    timestamp: str


class AuditRecord(BaseModel):
    event_id: str
    timestamp: str
    action_id: str
    agent_id: str
    action: str
    decision: str
    reason: str
    risk_score: float
    payload_json: str
    previous_hash: str
    current_hash: str