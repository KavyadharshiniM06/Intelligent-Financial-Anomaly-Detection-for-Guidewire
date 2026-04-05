from typing import Dict, Any, Tuple, List
from app.models.claim import Claim
from app.models.policy import Policy

def evaluate_rules(claim: Claim, policy: Policy, features: Dict[str, Any], max_amount: float = 50000.0) -> Tuple[float, List[str]]:
    """
    Evaluates the current claim against advanced business rules to compute a risk score and provide justifications.
    Uses a dynamic max_amount for high-value thresholding.
    """
    rule_score = 0.0
    triggered_rules = []
    
    amount = claim.claim_amount or 0

    # 1. Hard-Limit Check (Absolute Risk)
    if amount > max_amount:
        rule_score += 0.8 # Very high weight for exceeding limit
        triggered_rules.append(f"Hard-Limit Alert: Claim amount (${amount}) exceeds dynamic threshold (${max_amount})")

    # 2. New Policy Window Check
    if policy.start_date and claim.claim_date:
        days_since_start = (claim.claim_date - policy.start_date).days
        if 0 <= days_since_start <= 14:
            rule_score += 0.3
            triggered_rules.append(f"Policy-Window Alert: Claim within {days_since_start} days of inception")
            
    # 3. Safety Scoring (NCAP)
    ncap = getattr(policy, "ncap_rating", 4)
    if ncap >= 5:
        rule_score -= 0.1  # Safety discount
        triggered_rules.append(f"Safety Bonus: Vehicle has premium NCAP {ncap} safety rating")
    elif ncap <= 2:
        rule_score += 0.2
        triggered_rules.append(f"Risk Alert: Vehicle has low NCAP {ncap} safety rating")
        
    # 4. Severity vs Amount Inconsistency
    severity = getattr(claim, "incident_severity", "minor damage")
    if severity == "minor damage" and amount > 5000:
        rule_score += 0.4
        triggered_rules.append(f"Anomaly: High claim amount (${amount}) for 'Minor Damage' report")
    elif severity == "total loss" and amount < 2000:
        rule_score += 0.3
        triggered_rules.append(f"Anomaly: Suspiciously low claim amount (${amount}) for 'Total Loss'")
        
    # 5. Urban Density Risk
    density = features.get("region_density", 1)
    if density >= 4:
        rule_score += 0.2
        triggered_rules.append("Environment Alert: High-density urban region profile")
        
    # Cap the final score between 0.0 and 1.0
    rule_score = min(max(rule_score, 0.0), 1.0)
    
    return round(rule_score, 2), triggered_rules
