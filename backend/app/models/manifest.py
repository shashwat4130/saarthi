from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ActionManifest(BaseModel):
    action_id: str = Field(..., min_length=3)
    agent_id: str = Field(..., min_length=2)
    action: str = Field(..., min_length=2)
    arguments: Dict[str, Any]
    evidence: Dict[str, Any] = Field(default_factory=dict)
    intent_summary: Optional[str] = None