from typing import Dict, Any, Tuple, List
from app.models.claim import Claim
from app.models.policy import Policy

# Configurable thresholds for easy modification
RULE_1_DAYS_THRESHOLD = 7
RULE_1_RISK_SCORE = 0.3

RULE_2_CLAIMS_THRESHOLD = 3
RULE_2_RISK_SCORE = 0.4

RULE_3_LOW_AMOUNT_THRESHOLD = 150.0  # Defines what "unusually low" means
RULE_3_RISK_SCORE = 0.2

def evaluate_rules(claim: Claim, policy: Policy, features: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Evaluates the current claim against a set of business rules to compute a risk score.
    
    Returns:
        A tuple containing (rule_score, triggered_rules)
    """
    rule_score = 0.0
    triggered_rules = []
    
    # 1. Claim within 7 days of policy start -> add 0.3 risk
    if policy.start_date and claim.claim_date:
        days_since_start = (claim.claim_date - policy.start_date).days
        if 0 <= days_since_start <= RULE_1_DAYS_THRESHOLD:
            rule_score += RULE_1_RISK_SCORE
            triggered_rules.append(f"Claim submitted within {RULE_1_DAYS_THRESHOLD} days of policy start")
            
    # 2. More than 3 claims within last 10 days -> add 0.4 risk
    # This relies on the feature_engine providing 'recent_claims_count'
    recent_claims_count = features.get("recent_claims_count", 0)
    if recent_claims_count > RULE_2_CLAIMS_THRESHOLD:
        rule_score += RULE_2_RISK_SCORE
        triggered_rules.append(f"Frequent claims: {recent_claims_count} claims within the last 10 days")
        
    # 3. Average claim amount unusually low -> add 0.2 risk
    average_claim_amount = features.get("average_claim_amount", 0.0)
    # Check if the customer has a history of claims AND if the average is below the threshold
    if features.get("total_claims", 0) > 0 and average_claim_amount < RULE_3_LOW_AMOUNT_THRESHOLD:
        rule_score += RULE_3_RISK_SCORE
        triggered_rules.append(f"Average historical claim amount is unusually low (${average_claim_amount})")
        
    # Cap the final score between 0.0 and 1.0
    rule_score = min(max(rule_score, 0.0), 1.0)
    
    return round(rule_score, 2), triggered_rules
