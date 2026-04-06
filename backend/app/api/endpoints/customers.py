from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.customer import Customer
from app.models.policy import Policy
from app.schemas.customer import CustomerOverview
from app.db.session import get_db

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper: build a human-readable risk profile from raw data
# ---------------------------------------------------------------------------

DENSITY_LABELS = {
    0: "Rural",
    1: "Low Density",
    2: "Suburban",
    3: "Semi-Urban",
    4: "Dense Urban",
}


def _density_label(density: int) -> str:
    return DENSITY_LABELS.get(density, f"Density {density}")


def _compute_profile(customer: Customer, policy: Optional[Policy] = None) -> Tuple[str, str]:
    """
    Returns (profile_description, risk_tier) based on a combination of
    customer demographics and policy attributes.

    risk_tier is one of: "safe", "moderate", "high"
    """
    tags: list[str] = []
    risk_points = 0  # higher = riskier

    # --- Age factor ---
    if customer.age >= 40:
        tags.append("Experienced")
    elif customer.age <= 22:
        tags.append("Young Driver")
        risk_points += 1
    else:
        tags.append("Mid-Career")

    # --- Region density ---
    density = customer.region_density or 0
    if density >= 4:
        tags.append("Urban")
        risk_points += 2
    elif density >= 3:
        tags.append("Semi-Urban")
        risk_points += 1
    elif density <= 1:
        tags.append("Rural")

    # --- Policy tenure (veteran vs rookie) ---
    if policy and policy.start_date:
        tenure_days = (datetime.utcnow() - policy.start_date).days
        if tenure_days > 1825:  # > 5 years
            tags.append("Veteran")
        elif tenure_days <= 14:
            tags.append("New Policy")
            risk_points += 2
        elif tenure_days <= 90:
            tags.append("Recent Signup")
            risk_points += 1

    # --- NCAP safety ---
    if policy and policy.ncap_rating:
        if policy.ncap_rating >= 5:
            tags.append("Premium Safety")
        elif policy.ncap_rating <= 2:
            tags.append("Low Safety")
            risk_points += 1

    # --- Vehicle age ---
    if policy and policy.vehicle_age:
        if policy.vehicle_age >= 10:
            tags.append("Old Vehicle")
            risk_points += 1

    # --- Determine tier ---
    if risk_points >= 3:
        tier = "high"
    elif risk_points >= 1:
        tier = "moderate"
    else:
        tier = "safe"

    description = " · ".join(tags) if tags else "Standard Profile"
    return description, tier


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[CustomerOverview])
async def list_customers(db: AsyncSession = Depends(get_db)):
    """
    Returns all customers with their primary policy and a computed
    risk profile description for the demo Customer Registry view.
    """
    result = await db.execute(
        select(Customer).options(selectinload(Customer.policies))
    )
    customers = result.scalars().all()

    overviews: list[CustomerOverview] = []
    for cust in customers:
        # Pick the first (primary) policy, if any
        primary_policy: Optional[Policy] = cust.policies[0] if cust.policies else None

        description, tier = _compute_profile(cust, primary_policy)

        overviews.append(CustomerOverview(
            customer_id=cust.id,
            name=cust.name,
            age=cust.age,
            region_density=cust.region_density,
            policy_id=primary_policy.id if primary_policy else None,
            policy_type=primary_policy.policy_type if primary_policy else None,
            ncap_rating=primary_policy.ncap_rating if primary_policy else None,
            vehicle_age=primary_policy.vehicle_age if primary_policy else None,
            policy_start_date=primary_policy.start_date if primary_policy else None,
            density_label=_density_label(cust.region_density),
            profile_description=description,
            risk_tier=tier,
        ))

    return overviews
