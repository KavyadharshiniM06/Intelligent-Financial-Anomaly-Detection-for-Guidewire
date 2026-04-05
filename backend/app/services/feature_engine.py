import logging
import numpy as np
from typing import List, Dict, Any, Optional
from app.models.claim import Claim

logger = logging.getLogger(__name__)

FEATURE_ORDER = [
    "customer_age",
    "region_density",
    "policy_tenure",
    "vehicle_age",
    "ncap_rating",
    "incident_severity",
    "claim_amount",
    "days_since_policy_start",
    "velocity_1h",
    "amount_ratio",
    "ledger_flag",
    "behavioral_score"
]

DEFAULT_BEHAVIOR = {
    "velocity_1h": 0.0,
    "amount_ratio": 1.0,
    "ledger_flag": 0,
    "behavioral_score": 0.3
}

SEVERITY_MAP = {
    "trivial damage": 0,
    "minor damage": 1,
    "moderate damage": 2,
    "major damage": 3,
    "total loss": 4
}

SEVERITY_ALIASES = {
    "low": "minor damage",
    "medium": "moderate damage",
    "high": "major damage",
    "severe": "major damage",
    "totaled": "total loss",
    "complete loss": "total loss"
}

def get_feature_names() -> List[str]:
    return FEATURE_ORDER

def normalize_text(value: str) -> str:
    if not value or not isinstance(value, str):
        return ""
    return value.strip().lower()

def encode_severity(severity: str) -> int:
    normalized = normalize_text(severity)
    
    # Step 1: resolve aliases
    if normalized in SEVERITY_ALIASES:
        normalized = SEVERITY_ALIASES[normalized]
        
    # Step 2: map to ordinal
    if normalized in SEVERITY_MAP:
        return SEVERITY_MAP[normalized]
        
    # Step 3: fallback
    if normalized:
        logger.warning(f"Unknown incident_severity input: {severity}")
    return 0

def extract_claim_features(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts core domain features from insurance claim data."""
    if not claim_data:
        claim_data = {}
        
    return {
        "vehicle_age": float(claim_data.get("vehicle_age", 0.0)),
        "ncap_rating": int(claim_data.get("ncap_rating", 0)),
        "incident_severity": encode_severity(claim_data.get("incident_severity")),
        "claim_amount": float(claim_data.get("claim_amount", 0.0)),
        "days_since_policy_start": int(claim_data.get("days_since_policy_start", 0))
    }

def extract_customer_features(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts demographic and policy features from customer data."""
    if not customer_data:
        customer_data = {}
        
    return {
        "customer_age": int(customer_data.get("customer_age", 40)),
        "region_density": int(customer_data.get("region_density", 0)),
        "policy_tenure": float(customer_data.get("subscription_length", 0.0))
    }

def compute_behavioral_score(velocity_1h: float, amount_ratio: float, ledger_flag: int) -> float:
    # Normalize inputs before combining (simple normalization allowed)
    v = min(velocity_1h / 100.0, 1.0)
    r = min(amount_ratio / 5.0, 1.0)
    l = float(ledger_flag)

    w1, w2, w3 = 0.4, 0.4, 0.2

    return float(w1 * v + w2 * r + w3 * l)

def extract_behavioral_features(behavioral_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Extracts behavioral signals from transaction history records (PaySim context)."""
    if not behavioral_data:
        return DEFAULT_BEHAVIOR.copy()

    # User defined data, with defaults
    data = {
        "velocity_1h": float(behavioral_data.get("velocity_1h", DEFAULT_BEHAVIOR["velocity_1h"])),
        "amount_ratio": float(behavioral_data.get("amount_ratio", DEFAULT_BEHAVIOR["amount_ratio"])),
        "ledger_flag": int(behavioral_data.get("ledger_flag", DEFAULT_BEHAVIOR["ledger_flag"]))
    }
    data["behavioral_score"] = compute_behavioral_score(
        data["velocity_1h"], data["amount_ratio"], data["ledger_flag"]
    )
    return data

def build_feature_vector(inference_payload: Dict[str, Any]) -> np.ndarray:
    """
    Main entry point for decision engine to build a unified feature vector.
    Payload should contain keys: 'claim_data', 'customer_data', and optionally 'behavioral_data'.
    """
    if not inference_payload:
        inference_payload = {}
        
    # 1. Component Extraction
    claim = extract_claim_features(inference_payload.get("claim_data", {}))
    customer = extract_customer_features(inference_payload.get("customer_data", {}))
    behavior = extract_behavioral_features(inference_payload.get("behavioral_data"))
    
    # 2. Assemble pre-encoded numerical vector
    return np.array([
        customer["customer_age"],
        customer["region_density"],
        customer["policy_tenure"],
        claim["vehicle_age"],
        claim["ncap_rating"],
        claim["incident_severity"],
        claim["claim_amount"],
        claim["days_since_policy_start"],
        behavior["velocity_1h"],
        behavior["amount_ratio"],
        behavior["ledger_flag"],
        behavior["behavioral_score"]
    ]).reshape(1, -1)

# Keeping legacy helper for backward compatibility while migrating models
def compute_claim_features(claim: Claim, customer_claims: List[Claim]) -> Dict[str, Any]:
    """Legacy feature computation for backward compatibility."""
    previous_claims = [c for c in customer_claims if not hasattr(claim, "id") or c.id != claim.id]
    total_claims = len(previous_claims)
    
    if total_claims == 0:
        return {"total_claims": 0, "average_claim_amount": 0.0, "days_since_last_claim": -1}
        
    total_amount = sum(c.claim_amount for c in previous_claims)
    average_claim_amount = total_amount / total_claims
    recent_claims = sorted(previous_claims, key=lambda c: c.claim_date, reverse=True)
    days_since = max(0, (claim.claim_date - recent_claims[0].claim_date).days)
    
    return {
        "total_claims": total_claims,
        "average_claim_amount": round(average_claim_amount, 2),
        "days_since_last_claim": days_since,
        "recent_claims_count": len([c for c in previous_claims if 0 <= (claim.claim_date - c.claim_date).days <= 10])
    }
