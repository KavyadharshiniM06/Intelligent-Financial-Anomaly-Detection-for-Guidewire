import os
import joblib
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Constants for artifact persistence
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

# Global variables for loaded artifacts
_model = None
_scaler = None

def init_model():
    """Explicitly load the model and scaler artifacts into memory."""
    global _model, _scaler
    if _model is None or _scaler is None:
        try:
            logger.info(f"Loading ML artifacts from {os.path.dirname(MODEL_PATH)}")
            _model = joblib.load(MODEL_PATH)
            _scaler = joblib.load(SCALER_PATH)
            logger.info("ML artifacts loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load ML artifacts: {e}")
            raise RuntimeError("ML artifacts are missing or corrupt. Run training first.")

def predict_fraud(feature_vector: np.ndarray) -> float:
    """
    Predicts fraud probability using the loaded RandomForest model.
    Expects a pre-shaped (1, 12) numpy array.
    """
    init_model()
    
    # Scale features
    X_scaled = _scaler.transform(feature_vector)
    
    # Predict probability of class 1 (Fraud)
    # RandomForestClassifier.predict_proba returns [prob_0, prob_1]
    probs = _model.predict_proba(X_scaled)
    probability = float(probs[0][1])
    
    return round(probability, 4)

# Keep legacy helper for backward compatibility if needed, but mark as deprecated
def predict_fraud_legacy(features: Dict[str, Any]) -> float:
    """Mock fallback for older feature pipelines."""
    logger.warning("Using legacy mock prediction logic. Transition to feature vectors recommended.")
    total_claims = features.get("total_claims", 0)
    recent_claims_count = features.get("recent_claims_count", 0)
    
    # Simple heuristic to simulate some variance
    z = -3.0 + (0.5 * total_claims) + (1.2 * recent_claims_count)
    import math
    return round(1.0 / (1.0 + math.exp(-z)), 4)
