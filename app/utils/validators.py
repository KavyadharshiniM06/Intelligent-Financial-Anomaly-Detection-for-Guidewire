from datetime import datetime
from app.models.policy import Policy

def validate_policy_active(policy: Policy) -> bool:
    """
    Check if the current date is within the policy's start_date and end_date.
    Returns True if valid, raises ValueError if invalid.
    """
    now = datetime.utcnow()
    
    if policy.start_date and now < policy.start_date:
        raise ValueError("Policy is not active yet (start date is in the future).")
        
    if policy.end_date and now > policy.end_date:
        raise ValueError("Policy has expired.")
        
    return True

def validate_customer_policy(customer_id: int, policy: Policy) -> bool:
    """
    Ensure the policy belongs to the given customer_id.
    Returns True if valid, raises ValueError if invalid.
    """
    if policy.customer_id != customer_id:
        raise ValueError("Policy does not belong to the specified customer.")
        
    return True
