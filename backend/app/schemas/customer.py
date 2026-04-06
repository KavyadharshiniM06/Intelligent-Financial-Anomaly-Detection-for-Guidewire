from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CustomerOverview(BaseModel):
    """
    Schema for the Customer Registry view.
    Combines customer, policy, and a computed risk profile description.
    """
    customer_id: int = Field(..., description="Unique customer identifier")
    name: str = Field(..., description="Customer's full name")
    age: int = Field(..., description="Customer's age")
    region_density: int = Field(..., description="Population density of the customer's region (0-4)")
    policy_id: Optional[int] = Field(None, description="Associated policy ID")
    policy_type: Optional[str] = Field(None, description="Type of insurance policy")
    ncap_rating: Optional[int] = Field(None, description="Vehicle NCAP safety rating (1-5)")
    vehicle_age: Optional[int] = Field(None, description="Age of the insured vehicle in years")
    policy_start_date: Optional[datetime] = Field(None, description="Policy inception date")
    density_label: str = Field(..., description="Human-readable density level (e.g. Rural, Suburban, Urban)")
    profile_description: str = Field(..., description="Computed risk profile description (e.g. Safe Veteran, High Risk Urban)")
    risk_tier: str = Field(..., description="Risk tier classification: safe, moderate, or high")

    model_config = ConfigDict(from_attributes=True)
