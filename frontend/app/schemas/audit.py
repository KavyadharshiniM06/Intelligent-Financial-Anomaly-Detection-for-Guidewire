from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class AuditLogResponse(BaseModel):
    """
    Schema for viewing audit log details for a claim.
    """
    risk_score: float
    decision: str
    reasons: List[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
