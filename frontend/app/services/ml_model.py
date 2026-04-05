import math
from typing import Dict, Any

def predict_fraud(features: Dict[str, Any]) -> float:
    """
    Predicts the likelihood of a claim being fraudulent using a lightweight,
    placeholder Logistic Regression algorithm.
    
    Inputs:
        features: A dictionary containing computed features for the claim.
        
    Returns:
        float: A probability between 0.0 and 1.0.
    """
    # Extract features with safe fallbacks
    total_claims = features.get("total_claims", 0)
    average_claim_amount = features.get("average_claim_amount", 0.0)
    recent_claims_count = features.get("recent_claims_count", 0)
    
    # Mock model weights (simulating a pre-trained logistic regression)
    # In a production setting, you would load a pickled Scikit-Learn or XGBoost model
    bias = -3.5  # Base log-odds (assumes baseline is unlikely to be fraud)
    w_total_claims = 0.05
    w_avg_amount = 0.001
    w_recent_claims = 0.8
    
    # Calculate linear combination (z = w0 + w1*x1 + w2*x2 + ...)
    z = (bias + 
         (w_total_claims * total_claims) + 
         (w_avg_amount * average_claim_amount) + 
         (w_recent_claims * recent_claims_count))
         
    # Apply the Sigmoid activated function to squish `z` into a 0 -> 1 probability
    try:
        probability = 1.0 / (1.0 + math.exp(-z))
    except OverflowError:
        # Handles math overflow: if z is a massive negative number, probability is practically 0.
        probability = 0.0 if z < 0 else 1.0
        
    return round(probability, 4)
