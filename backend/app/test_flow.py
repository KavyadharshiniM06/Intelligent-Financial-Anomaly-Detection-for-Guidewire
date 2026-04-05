from datetime import datetime, timedelta

from app.utils.validators import validate_policy_active, validate_customer_policy
from app.services.feature_engine import compute_claim_features
from app.services.rule_engine import evaluate_rules
from app.services.ml_model import predict_fraud
from app.services.decision_engine import make_decision

# Mock objects (simulate DB data)

class Obj:
    def __init__(self, **entries):
        self.__dict__.update(entries)

policy = Obj(
    start_date=datetime.now() - timedelta(days=2),
    end_date=datetime.now() + timedelta(days=365),
    customer_id=1
)

claim = Obj(
    claim_amount=500,
    claim_date=datetime.now(),
    customer_id=1
)

previous_claims = [
    Obj(claim_date=datetime.now() - timedelta(days=1), claim_amount=200),
    Obj(claim_date=datetime.now() - timedelta(days=3), claim_amount=300),
]

# Step 1: Validation
validate_policy_active(policy)
validate_customer_policy(1, policy)

# Step 2: Feature Engineering
features = compute_claim_features(claim, previous_claims)

# Step 3: Rule Engine
rule_score, reasons = evaluate_rules(claim, policy, features)

# Step 4: ML Model
ml_score = predict_fraud(features)

# Step 5: Decision
final_score, decision = make_decision(ml_score, rule_score)

# Output
print({
    "risk_score": final_score,
    "decision": decision,
    "reasons": reasons
})