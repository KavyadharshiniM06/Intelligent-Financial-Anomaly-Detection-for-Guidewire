import os
import logging
import joblib
import numpy as np
from typing import Tuple, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

logger = logging.getLogger(__name__)

# Constants for artifact persistence
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

def train_risk_model(X: np.ndarray, y: np.ndarray) -> Tuple[Any, StandardScaler]:
    """
    Trains a risk evaluation model using Scikit-learn and saves the artifacts.
    
    Args:
        X: Feature matrix of shape (N, 12).
        y: Target array of shape (N,).
        
    Returns:
        trained_model: The fitted Scikit-learn classifier.
        scaler: The fitted StandardScaler.
    """
    logger.info("Initializing risk model training pipeline...")
    
    # 1. Split Data into Training and Validation Sets
    # Utilizing stratification to handle any inherent class imbalances (fraud is usually rare)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 2. Scale Features
    # Standardizing features by removing the mean and scaling to unit variance
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    from sklearn.metrics import f1_score, confusion_matrix, classification_report

    # 3. Model Registration & Training
    model = RandomForestClassifier(
        n_estimators=200, 
        class_weight="balanced_subsample",
        random_state=42
    )
    
    logger.info(f"Training {model.__class__.__name__} with shape {X_train_scaled.shape}...")
    model.fit(X_train_scaled, y_train)
    
    # 4. Evaluation (Probability-based decisions)
    # Using predict_proba instead of default predict()
    probs = model.predict_proba(X_test_scaled)[:, 1]
    
    print("\n--- Probability Distribution Analysis ---")
    print(f"Min Probability:  {np.min(probs):.4f}")
    print(f"Max Probability:  {np.max(probs):.4f}")
    print(f"Mean Probability: {np.mean(probs):.4f}")
    
    # Generate binary predictions based on the new lowest risk threshold (0.15) to evaluate Recall
    # All INVESTIGATE and REJECT outcomes count as positive anomaly labels
    y_pred = (probs > 0.15).astype(int)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # 5. Output Metrics Clearly
    print("\n" + "="*50)
    print("  REBALANCED RISK MODEL EVALUATION METRICS  ")
    print("="*50)
    print(f"Algorithm:       {model.__class__.__name__}")
    print(f"Samples Tested:  {len(y_test)}")
    print("-" * 50)
    print(f"Accuracy:        {acc:.4f}  ({acc * 100:.2f}%)")
    print(f"Precision:       {prec:.4f}  ({prec * 100:.2f}%)")
    print(f"Recall:          {rec:.4f}  ({rec * 100:.2f}%)")
    print(f"F1-score:        {f1:.4f}  ({f1 * 100:.2f}%)")
    print("-" * 50)
    print("Confusion Matrix:")
    print(f"  True Positives  (Caught Fraud):  {tp}")
    print(f"  False Positives (False Alarm):   {fp}")
    print(f"  True Negatives  (Correct OK):    {tn}")
    print(f"  False Negatives (Missed Fraud):  {fn}")
    print("-" * 50)
    print("Classification Report (Threshold 0.15):")
    print(classification_report(y_test, y_pred, zero_division=0))
    print("="*50 + "\n")
    
    # Decision Threshold Logic (DO NOT USE DEFAULT predict())
    def apply_decision_threshold(prob):
        if prob > 0.5:
            return "REJECT"
        elif prob > 0.15:
            return "INVESTIGATE"
        else:
            return "APPROVE"
            
    decisions = [apply_decision_threshold(p) for p in probs]
    
    print("Sample Decision Outputs (Threshold Logic):")
    for i in range(min(10, len(probs))):
        prob = probs[i]
        print(f"  Claim {i+1}: Risk Probability = {prob:.4f} -> Decision = {decisions[i]}")
    print("="*50 + "\n")
    
    # Detailed logging push
    logger.info(f"Model Training Complete. Acc: {acc:.4f}, Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}")

    
    # 6. Save Artifacts for Inference Using Joblib
    logger.info("Saving trained model and scaler artifacts...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    logger.info(f"Artifacts successfully saved to {os.path.dirname(MODEL_PATH)}")
    
    return model, scaler

def load_model() -> Tuple[Any, StandardScaler]:
    """
    Loads the trained model and scaler from disk.
    
    Returns:
        trained_model: The loaded Scikit-learn Classifier.
        scaler: The loaded StandardScaler.
    """
    logger.info(f"Attempting to load artifacts from {os.path.dirname(MODEL_PATH)}...")
    
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        logger.error("Missing artifacts. Both model.pkl and scaler.pkl are required.")
        raise FileNotFoundError("Model or scaler artifact not found. Please train the model first.")
        
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    logger.info("Successfully loaded model and scaler artifacts.")
    
    return model, scaler
