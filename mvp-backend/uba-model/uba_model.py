import pickle
import os
import pandas as pd
import numpy as np

# Path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
_model = None

def load_model():
    """Load the trained model from disk"""
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
        else:
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
    return _model

def predict_risk_score(behavior_data):
    """
    Predict risk score for a single user behavior instance.
    
    Args:
        behavior_data (dict): Dictionary containing feature values
        
    Returns:
        dict: containing 'risk_score' (0-100) and 'anomaly_score' (raw)
    """
    model = load_model()
    
    # Ensure feature order matches training
    features = [
        'login_hour', 'location_id', 'is_new_device', 'actions_count',
        'files_accessed', 'session_duration', 'failed_logins', 'sensitive_access'
    ]
    
    # Prepare input dataframe
    try:
        data = {feat: [behavior_data.get(feat, 0)] for feat in features}
        df = pd.DataFrame(data)
        
        # Get raw anomaly score (decision_function)
        # Isolation Forest: lower score = more anomalous (negative values are anomalies)
        # We want to convert this to a 0-100 risk score
        
        raw_score = model.decision_function(df)[0]
        is_anomaly = model.predict(df)[0] == -1
        
        # Convert decision function to risk score (0-100)
        # Typical decision scores range from -0.5 (very anomalous) to 0.5 (very normal)
        # We want to map:
        # 0.2 -> 0 (Safe)
        # 0.0 -> 30 (Warning)
        # -0.2 -> 80 (High Risk)
        
        # Clip to expected range then normalize
        score = -raw_score # Invert so higher is riskier
        
        # Map roughly from [-0.2, 0.3] to [0, 100]
        # Adjusted formula based on typical isolation forest output
        normalized_risk = (score + 0.2) * 200 
        
        # Clamp between 0 and 100
        final_risk = max(0, min(100, normalized_risk))
        
        # Force high risk if predicted as anomaly
        if is_anomaly and final_risk < 50:
            final_risk = 50 + final_risk
            
        return {
            'risk_score': int(final_risk),
            'anomaly_score': float(raw_score),
            'is_anomaly': bool(is_anomaly)
        }
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return {'risk_score': 0, 'anomaly_score': 0, 'is_anomaly': False}
