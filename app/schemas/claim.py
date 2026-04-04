from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List

class ClaimCreate(BaseModel):
    """
    Schema for validating incoming claim JSON payloads.
    """
    customer_id: int = Field(..., description="ID of the customer submitting the claim")
    policy_id: int = Field(..., description="ID of the associated insurance policy")
    claim_amount: float = Field(..., gt=0, description="The monetary amount of the claim. Must be greater than 0.")
    claim_date: datetime = Field(
        default_factory=datetime.utcnow, 
        description="The exact datetime the claim occurred. Defaults to now."
    )

class ClaimResponse(BaseModel):
    """
    Schema for formatting the response after processing a claim.
    """
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Computed risk score formatted between 0.0 and 1.0")
    decision: str = Field(..., description="The final automated action taken by the decision engine")
    reasons: List[str] = Field(
        default_factory=list, 
        description="Textual reasons justifying the risk score and decision"
    )
    confidence: str = Field(..., description="The textual confidence level of the risk (e.g. LOW RISK, MEDIUM RISK, HIGH RISK)")

    
    # Allows reading data straight from SQLAlchemy models if needed
    model_config = ConfigDict(from_attributes=True)

class ClaimDetail(BaseModel):
    """
    Schema for viewing claim details via the API.
    """
    id: int = Field(..., description="The unique identifier for the claim")
    customer_id: int = Field(..., description="ID of the customer submitting the claim")
    policy_id: int = Field(..., description="ID of the associated insurance policy")
    claim_amount: float = Field(..., description="The monetary amount of the claim")
    claim_date: datetime = Field(..., description="The exact datetime the claim occurred")
    status: str = Field(..., description="Current status of the claim")
    created_at: datetime = Field(..., description="Timestamp of when the claim was recorded in the system")

    model_config = ConfigDict(from_attributes=True)
