"""
Nafath UBA (User Behavior Analytics) - ML Model
================================================
A working Isolation Forest model for detecting anomalous user behavior.

Model: Nafath-UBA-v2.1
Algorithm: Isolation Forest (Unsupervised Anomaly Detection)
Features: 8 behavioral features
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
import pickle
from datetime import datetime, timedelta
import random

# =====================================
# 1. GENERATE SYNTHETIC TRAINING DATA
# =====================================

def generate_normal_behavior(n_samples=1000):
    """Generate normal user behavior patterns"""
    np.random.seed(42)
    
    data = {
        # Login hour (8-18 normal working hours)
        'login_hour': np.random.normal(13, 2, n_samples).clip(8, 18),
        
        # Location (0-2: known locations - Riyadh, Jeddah, Dammam)
        'location_id': np.random.choice([0, 1, 2], n_samples, p=[0.7, 0.2, 0.1]),
        
        # Device familiarity (0: known, 1: new) - mostly known devices
        'is_new_device': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        
        # Number of actions per session (5-30 normal)
        'actions_count': np.random.normal(15, 5, n_samples).clip(5, 30),
        
        # Files accessed (1-10 normal)
        'files_accessed': np.random.normal(5, 2, n_samples).clip(1, 10),
        
        # Session duration in minutes (15-120 normal)
        'session_duration': np.random.normal(60, 20, n_samples).clip(15, 120),
        
        # Failed login attempts (0-1 normal)
        'failed_logins': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        
        # Sensitive data access (0-2 normal)
        'sensitive_access': np.random.choice([0, 1, 2], n_samples, p=[0.6, 0.3, 0.1])
    }
    
    return pd.DataFrame(data)


def generate_anomalous_behavior(n_samples=50):
    """Generate anomalous/attack behavior patterns"""
    np.random.seed(123)
    
    data = {
        # Login at unusual hours (0-6 AM or late night)
        'login_hour': np.random.choice([2, 3, 4, 23, 0, 1], n_samples),
        
        # Location (3-5: unknown/foreign locations)
        'location_id': np.random.choice([3, 4, 5], n_samples),
        
        # New/unknown device
        'is_new_device': np.ones(n_samples),
        
        # Unusual number of actions (too many or too few)
        'actions_count': np.random.choice(
            list(range(80, 200)) + list(range(0, 3)), n_samples
        ),
        
        # Many files accessed (data exfiltration pattern)
        'files_accessed': np.random.randint(30, 100, n_samples),
        
        # Very short or very long sessions
        'session_duration': np.random.choice(
            list(range(1, 5)) + list(range(240, 480)), n_samples
        ),
        
        # Multiple failed login attempts
        'failed_logins': np.random.randint(3, 10, n_samples),
        
        # High sensitive data access
        'sensitive_access': np.random.randint(5, 15, n_samples)
    }
    
    return pd.DataFrame(data)


# =====================================
# 2. TRAIN ISOLATION FOREST MODEL
# =====================================

def train_model():
    """Train the Isolation Forest model on normal behavior"""
    print("=" * 50)
    print("  Nafath UBA Model Training")
    print("=" * 50)
    
    # Generate training data (normal behavior only)
    print("\n[1] Generating synthetic normal behavior data...")
    normal_data = generate_normal_behavior(1000)
    print(f"    Generated {len(normal_data)} normal behavior samples")
    
    # Prepare features
    feature_columns = [
        'login_hour', 'location_id', 'is_new_device', 'actions_count',
        'files_accessed', 'session_duration', 'failed_logins', 'sensitive_access'
    ]
    X_train = normal_data[feature_columns]
    
    # Scale features
    print("\n[2] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train Isolation Forest
    print("\n[3] Training Isolation Forest model...")
    model = IsolationForest(
        n_estimators=100,        # Number of trees
        contamination=0.05,      # Expected proportion of anomalies
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled)
    print("    Model trained successfully!")
    
    # Save model and scaler
    print("\n[4] Saving model and scaler...")
    with open('uba_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('uba_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    print("    Saved: uba_model.pkl, uba_scaler.pkl")
    
    return model, scaler


# =====================================
# 3. EVALUATE MODEL
# =====================================

def evaluate_model(model, scaler):
    """Evaluate model on test data"""
    print("\n[5] Evaluating model performance...")
    
    # Generate test data
    normal_test = generate_normal_behavior(200)
    anomaly_test = generate_anomalous_behavior(50)
    
    feature_columns = [
        'login_hour', 'location_id', 'is_new_device', 'actions_count',
        'files_accessed', 'session_duration', 'failed_logins', 'sensitive_access'
    ]
    
    # Predict on normal data
    X_normal = scaler.transform(normal_test[feature_columns])
    normal_preds = model.predict(X_normal)
    normal_accuracy = (normal_preds == 1).sum() / len(normal_preds)
    
    # Predict on anomaly data
    X_anomaly = scaler.transform(anomaly_test[feature_columns])
    anomaly_preds = model.predict(X_anomaly)
    anomaly_detection_rate = (anomaly_preds == -1).sum() / len(anomaly_preds)
    
    print(f"\n    Results:")
    print(f"    - Normal behavior correctly classified: {normal_accuracy:.1%}")
    print(f"    - Anomalies correctly detected: {anomaly_detection_rate:.1%}")
    print(f"    - Overall accuracy: {(normal_accuracy + anomaly_detection_rate) / 2:.1%}")
    
    return normal_accuracy, anomaly_detection_rate


# =====================================
# 4. PREDICT FUNCTION (For API/Demo)
# =====================================

def load_model():
    """Load trained model and scaler"""
    with open('uba_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('uba_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler


def predict_risk_score(behavior_data):
    """
    Predict risk score for a user behavior.
    
    Args:
        behavior_data: dict with keys:
            - login_hour (0-23)
            - location_id (0-5, 0-2 known, 3-5 unknown)
            - is_new_device (0 or 1)
            - actions_count (int)
            - files_accessed (int)
            - session_duration (minutes)
            - failed_logins (int)
            - sensitive_access (int)
    
    Returns:
        dict with risk_score (0-100) and status
    """
    model, scaler = load_model()
    
    # Prepare features
    features = np.array([[
        behavior_data.get('login_hour', 12),
        behavior_data.get('location_id', 0),
        behavior_data.get('is_new_device', 0),
        behavior_data.get('actions_count', 15),
        behavior_data.get('files_accessed', 5),
        behavior_data.get('session_duration', 60),
        behavior_data.get('failed_logins', 0),
        behavior_data.get('sensitive_access', 0)
    ]])
    
    # Scale and predict
    features_scaled = scaler.transform(features)
    
    # Get anomaly score (-1 to 0, where more negative = more anomalous)
    anomaly_score = model.decision_function(features_scaled)[0]
    
    # Convert to risk score (0-100)
    # decision_function returns negative for anomalies, positive for normal
    # We convert this to a 0-100 risk score
    risk_score = int(max(0, min(100, (1 - (anomaly_score + 0.5)) * 100)))
    
    # Determine status
    if risk_score < 30:
        status = "normal"
        status_ar = "سلوك طبيعي"
    elif risk_score < 60:
        status = "suspicious"
        status_ar = "سلوك مشبوه"
    else:
        status = "threat"
        status_ar = "تهديد محتمل"
    
    return {
        "risk_score": risk_score,
        "status": status,
        "status_ar": status_ar,
        "anomaly_score": float(anomaly_score),
        "prediction": "anomaly" if risk_score >= 50 else "normal"
    }


# =====================================
# 5. DEMO SCENARIOS
# =====================================

def demo():
    """Run demo scenarios"""
    print("\n" + "=" * 50)
    print("  DEMO: Risk Score Predictions")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Normal Employee Login",
            "data": {
                "login_hour": 9,
                "location_id": 0,  # Riyadh
                "is_new_device": 0,
                "actions_count": 12,
                "files_accessed": 3,
                "session_duration": 45,
                "failed_logins": 0,
                "sensitive_access": 1
            }
        },
        {
            "name": "Suspicious Activity",
            "data": {
                "login_hour": 2,  # 2 AM
                "location_id": 3,  # Unknown location
                "is_new_device": 1,
                "actions_count": 85,
                "files_accessed": 25,
                "session_duration": 10,
                "failed_logins": 2,
                "sensitive_access": 5
            }
        },
        {
            "name": "Potential Attack",
            "data": {
                "login_hour": 3,  # 3 AM
                "location_id": 5,  # Foreign
                "is_new_device": 1,
                "actions_count": 150,
                "files_accessed": 80,
                "session_duration": 300,
                "failed_logins": 5,
                "sensitive_access": 12
            }
        }
    ]
    
    for scenario in scenarios:
        result = predict_risk_score(scenario["data"])
        print(f"\n  Scenario: {scenario['name']}")
        print(f"  └─ Risk Score: {result['risk_score']}/100")
        print(f"  └─ Status: {result['status_ar']}")
        print(f"  └─ Anomaly Score: {result['anomaly_score']:.3f}")


# =====================================
# MAIN
# =====================================

if __name__ == "__main__":
    # Train model
    model, scaler = train_model()
    
    # Evaluate
    evaluate_model(model, scaler)
    
    # Run demo
    demo()
    
    print("\n" + "=" * 50)
    print("  Model ready! Use predict_risk_score() for predictions")
    print("=" * 50)
