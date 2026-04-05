import logging
import pandas as pd
import numpy as np
from typing import Optional, Tuple

try:
    from app.services.feature_engine import build_feature_vector
except ImportError:
    # For testing compatibility depending on module execution context
    from backend.app.services.feature_engine import build_feature_vector

logger = logging.getLogger(__name__)

def load_insurance_data(path: str) -> pd.DataFrame:
    """
    Loads and cleans the Insurance Claims dataset.
    
    Args:
        path: File path to the CSV dataset.
        
    Returns:
        pd.DataFrame containing the cleaned insurance data.
    """
    try:
        df = pd.read_csv(path)
        
        # Drop columns that are intuitively irrelevant for ML modeling
        # Identifiers and primary keys typically cause overfitting
        cols_to_drop = ['policy_id'] 
        existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
        if existing_cols_to_drop:
            df = df.drop(columns=existing_cols_to_drop)
            
        # Basic missing value handling
        # Refill numeric NaNs with dataset median to reduce outlier impact
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Refill categorical NaNs with a safe fallback placeholder
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        df[categorical_cols] = df[categorical_cols].fillna("Unknown")
        
        logger.info(f"Successfully loaded and cleaned insurance data. Shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load insurance data from {path}: {e}")
        raise

def load_paysim_data(path: str) -> pd.DataFrame:
    """
    Loads and cleans the PaySim financial transaction dataset.
    """
    try:
        # Load the large file
        df = pd.read_csv(path)
        
        # We KEEP 'nameOrig' for now because it's required for behavioral aggregation in prepare_training_data
        # We only drop truly irrelevant or leaking columns at this stage
        cols_to_drop = ['isFlaggedFraud']
        existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
        if existing_cols_to_drop:
            df = df.drop(columns=existing_cols_to_drop)
            
        # Basic cleaning
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0.0)
        
        logger.info(f"Successfully loaded PaySim data. Shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load PaySim data from {path}: {e}")
        raise

def prepare_training_data(insurance_df: pd.DataFrame, paysim_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates training feature matrix X and target array y.
    """
    logger.info("Starting training data preparation...")
    
    # 1. Aggregate behavioral data per customer from PaySim history
    # We group by nameOrig to get per-customer behavioral statistics
    logger.info("Aggregating PaySim behavioral signals...")
    
    # velocity_1h: max transactions per step (hour) for an agent
    velocity = paysim_df.groupby(['nameOrig', 'step']).size().groupby('nameOrig').max().rename('velocity_1h')
    
    # amount_ratio: current transaction relative to user's average
    mean_amount = paysim_df.groupby('nameOrig')['amount'].mean()
    max_amount = paysim_df.groupby('nameOrig')['amount'].max()
    amount_ratio = (max_amount / (mean_amount + 1e-9)).rename('amount_ratio')
    
    # ledger_flag: detect balance discrepancies
    paysim_df['ledger_err'] = (paysim_df['oldbalanceOrg'] - paysim_df['amount'] - paysim_df['newbalanceOrig']).abs() > 0.01
    ledger_flag = paysim_df.groupby('nameOrig')['ledger_err'].max().astype(int).rename('ledger_flag')

    # Combine behavioral signals
    behaviors = pd.concat([velocity, amount_ratio, ledger_flag], axis=1).reset_index(drop=True)
    
    # 2. Assign behavioral data to insurance claims (simulated domain intersection)
    # We use random sampling to simulate a linked transaction history for each policy holder
    behaviors_sampled = behaviors.sample(n=len(insurance_df), replace=True, random_state=42).reset_index(drop=True)
    
    X_list = []
    y_list = []
    
    logger.info(f"Generating feature vectors for {len(insurance_df)} entries...")
    
    for i, row in insurance_df.iterrows():
        target_val = int(row.get('claim_status', 0))
        beh = behaviors_sampled.iloc[i].to_dict()
        
        payload = {
            "claim_data": row.to_dict(),
            "customer_data": row.to_dict(),
            "behavioral_data": beh
        }
        
        vector = build_feature_vector(payload)
        X_list.append(vector[0])
        y_list.append(target_val)
        
    X = np.array(X_list)
    y = np.array(y_list)
    
    logger.info(f"Feature matrix generated. X shape: {X.shape}, y shape: {y.shape}")
    return X, y
