from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    ERROR = "ERROR"


class Discrepancy(BaseModel):
    field: str
    agent_value: Any
    trusted_value: Any
    delta: Optional[float] = None
    reason: str


class VerificationReport(BaseModel):
    verified: bool
    status: VerificationStatus
    checked_fields: List[str]
    discrepancies: List[Discrepancy] = Field(default_factory=list)
    execution_time_ms: float = 0.0