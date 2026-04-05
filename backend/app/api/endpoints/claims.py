from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.claim import ClaimCreate, ClaimResponse, ClaimDetail
from app.models.claim import Claim, ClaimStatus
from app.models.policy import Policy
from app.models.customer import Customer
from app.db.session import get_db

from app.utils.validators import validate_policy_active, validate_customer_policy
from app.services.feature_engine import compute_claim_features
from app.services.rule_engine import evaluate_rules
from app.services.ml_model import predict_fraud
from app.services.decision_engine import make_decision
from app.services.audit_logger import log_decision
from app.models.system_config import SystemConfig

router = APIRouter()
@router.post("/submit", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def submit_claim(claim_in: ClaimCreate, db: AsyncSession = Depends(get_db)):
    # 1. Fetch related Policy, Customer, and System Configuration
    policy_res = await db.execute(select(Policy).filter(Policy.id == claim_in.policy_id))
    policy = policy_res.scalars().first()
    
    customer_res = await db.execute(select(Customer).filter(Customer.id == claim_in.customer_id))
    customer = customer_res.scalars().first()
    
    config_res = await db.execute(select(SystemConfig).filter(SystemConfig.id == "MAX_CREDIBLE_AMOUNT"))
    max_amount_config = config_res.scalars().first()
    max_amount = max_amount_config.value if max_amount_config else 50000.0
    
    if not policy or not customer:
        raise HTTPException(status_code=404, detail="Policy or Customer not found.")
        
    # 2. Run Validators
    try:
        validate_customer_policy(claim_in.customer_id, policy)
        validate_policy_active(policy)
    except ValueError as e:
        # Translate generic python value errors into clean 400 Bad Requests
        raise HTTPException(status_code=400, detail=str(e))
        
    # 3. Create provisional Claim instance in the DB (to generate an ID)
    new_claim = Claim(
        policy_id=claim_in.policy_id,
        customer_id=claim_in.customer_id,
        claim_amount=claim_in.claim_amount,
        claim_date=claim_in.claim_date.replace(tzinfo=None),
        incident_severity=claim_in.incident_severity,
        status=ClaimStatus.SUBMITTED
    )
    
    db.add(new_claim)
    await db.commit()         # Commits the claim to assign an auto-incremented ID
    await db.refresh(new_claim)
    
    # 4. Fetch historical claims for this customer using SQLAlchemy
    claims_result = await db.execute(
        select(Claim).filter(Claim.customer_id == claim_in.customer_id)
    )
    customer_claims = claims_result.scalars().all()
    
    # 5. Execute Pipeline Core
    # A. Build the unified 12-feature vector for the ML model
    # Priority: Use DB values if present, else fallback to payload, then defaults.
    inference_payload = {
        "claim_data": {
            "vehicle_age": getattr(policy, "vehicle_age", claim_in.vehicle_age),
            "ncap_rating": getattr(policy, "ncap_rating", claim_in.ncap_rating),
            "incident_severity": claim_in.incident_severity,
            "claim_amount": claim_in.claim_amount,
            "days_since_policy_start": (new_claim.claim_date - policy.start_date).days
        },
        "customer_data": {
            "customer_age": getattr(customer, "age", claim_in.customer_age),
            "region_density": getattr(customer, "region_density", claim_in.region_density),
            "subscription_length": (new_claim.claim_date - policy.start_date).days / 365.25
        },
        "behavioral_data": None 
    }
    from app.services.feature_engine import build_feature_vector
    feature_vector = build_feature_vector(inference_payload)
    
    # B. ML Prediction (RandomForest probability)
    ml_score = predict_fraud(feature_vector)
    
    # C. Rule Evaluation (Legacy features for backward rules compatibility)
    legacy_features = compute_claim_features(new_claim, customer_claims)
    rule_score, reasons = evaluate_rules(new_claim, policy, legacy_features, max_amount=max_amount)
    
    # D. Final Decision Logic
    final_score, decision = make_decision(ml_score, rule_score)
    
    # E. Hard-Override for Excessive Amounts
    if claim_in.claim_amount > (max_amount * 2):
        decision = "REJECT"
        if "Hard-Limit Alert" not in " ".join(reasons):
            reasons.append(f"Security Override: Claim amount greatly exceeds credible limit (${max_amount})")
    
    # 6. Update the original claim status corresponding to the decision map
    if decision == "APPROVE":
        new_claim.status = ClaimStatus.APPROVED
    elif decision == "REJECT":
        new_claim.status = ClaimStatus.REJECTED
    else:
        new_claim.status = ClaimStatus.INVESTIGATING
        
    await db.commit()  # Save status update
    
    # 7. Log decision asynchronously (Commit is handled inside log_decision)
    await log_decision(
        db=db,
        claim_id=new_claim.id,
        risk_score=final_score,
        decision=decision,
        reasons=reasons
    )
    
    # 8. Determine confidence level
    if final_score < 0.3:
        confidence = "LOW RISK"
    elif 0.3 <= final_score <= 0.7:
        confidence = "MEDIUM RISK"
    else:
        confidence = "HIGH RISK"
        
    return ClaimResponse(
        claim_id=new_claim.id,
        risk_score=final_score,
        decision=decision,
        reasons=reasons,
        confidence=confidence
    )

@router.get("/{claim_id}", response_model=ClaimDetail)
async def get_claim(claim_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve details for a specific claim by ID.
    """
    result = await db.execute(select(Claim).filter(Claim.id == claim_id))
    claim = result.scalars().first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")
        
    return claim

