from typing import Tuple

# Standardized outcomes
DECISION_APPROVE = "APPROVE"
DECISION_INVESTIGATE = "INVESTIGATE"
DECISION_REJECT = "REJECT"

def make_decision(ml_score: float, rule_score: float) -> Tuple[float, str]:
    """
    Combines the machine learning probability and rule-based risk scores 
    to make an automated final decision on an insurance claim.
    
    Inputs:
        ml_score: The probability output from the ML model (0 to 1).
        rule_score: The computed risk score from the business rules (0 to 1).
        
    Returns:
        A tuple of (final_score, decision_action)
    """
    # Define weights for the scores
    ml_weight = 0.6
    rule_weight = 0.4
    
    # Calculate the weighted average
    final_score = (ml_weight * ml_score) + (rule_weight * rule_score)
    final_score = round(final_score, 4)
    
    # Evaluate thresholds to generate the final decision
    if final_score < 0.3:
        decision = DECISION_APPROVE
    elif 0.3 <= final_score <= 0.7:
        decision = DECISION_INVESTIGATE
    else:
        decision = DECISION_REJECT
        
    return final_score, decision
