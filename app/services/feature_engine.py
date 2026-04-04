from typing import List, Dict, Any
from app.models.claim import Claim

def compute_claim_features(claim: Claim, customer_claims: List[Claim]) -> Dict[str, Any]:
    """
    Computes risk-related features for a given claim based on historical customer claims.
    
    Inputs:
        claim: The current Claim instance being processed.
        customer_claims: A list of previous Claim instances belonging to the customer.
        
    Returns:
        A dictionary containing computed features.
    """
    # Ensure the current claim is not counted inside the historical claims
    previous_claims = []

    for c in customer_claims:
        if hasattr(claim, "id") and hasattr(c, "id"):
            if c.id != claim.id:
                previous_claims.append(c)
        else:
            previous_claims.append(c)
    
    total_claims = len(previous_claims)
    
    # Edge Case: Customer has no previous claims
    if total_claims == 0:
        return {
            "total_claims": 0,
            "average_claim_amount": 0.0,
            "days_since_last_claim": -1  # -1 or None can represent 'no previous claims'
        }
        
    total_amount = sum(c.claim_amount for c in previous_claims)
    average_claim_amount = total_amount / total_claims
    
    # Find the most recent historical claim
    # Sorting by claim_date descending so index 0 is the newest historical claim
    recent_claims = sorted(previous_claims, key=lambda c: c.claim_date, reverse=True)
    last_claim = recent_claims[0]
    
    # Compute days since last claim
    time_difference = claim.claim_date - last_claim.claim_date
    # Using max(0, ...) protects against potential negative values if dates are out of order
    days_since_last_claim = max(0, time_difference.days)
    
    # Calculate how many claims occurred in the last 10 days
    recent_claims_10_days = [c for c in previous_claims if 0 <= (claim.claim_date - c.claim_date).days <= 10]
    recent_claims_count = len(recent_claims_10_days)
    
    return {
        "total_claims": total_claims,
        "average_claim_amount": round(average_claim_amount, 2),
        "days_since_last_claim": days_since_last_claim,
        "recent_claims_count": recent_claims_count
    }
