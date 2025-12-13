import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle
import os
import random

# Set random seed for reproducibility
np.random.seed(42)

def generate_normal_data(n=4500):
    """Generate normal user behavior data"""
    data = {
        'login_hour': np.random.normal(12, 3, n).astype(int),  # Centered around noon
        'location_id': np.random.choice([0, 1], p=[0.8, 0.2], size=n),  # Mostly Riyadh (0) or Jeddah (1)
        'is_new_device': np.random.choice([0, 1], p=[0.9, 0.1], size=n),  # Mostly known devices
        'actions_count': np.random.normal(10, 5, n).astype(int),
        'files_accessed': np.random.poisson(2, n),
        'session_duration': np.random.normal(30, 10, n).astype(int),
        'failed_logins': np.random.choice([0, 1], p=[0.95, 0.05], size=n),
        'sensitive_access': np.random.choice([0, 1], p=[0.9, 0.1], size=n)
    }
    
    # Clip values to realistic ranges
    df = pd.DataFrame(data)
    df['login_hour'] = df['login_hour'].clip(6, 22)  # Business hours
    df['actions_count'] = df['actions_count'].clip(1, 40)
    df['files_accessed'] = df['files_accessed'].clip(0, 10)
    df['session_duration'] = df['session_duration'].clip(5, 120)
    
    return df

def generate_anomaly_data(n=500):
    """Generate anomalous user behavior data"""
    data = {
        'login_hour': np.random.choice([0, 1, 2, 3, 4, 23], size=n),  # Late night
        'location_id': np.random.randint(2, 5, size=n),  # Unknown locations (2, 3, 4)
        'is_new_device': np.random.choice([0, 1], p=[0.2, 0.8], size=n),  # Mostly new devices
        'actions_count': np.random.normal(50, 15, n).astype(int),  # High activity
        'files_accessed': np.random.normal(15, 5, n).astype(int),  # Data exfiltration?
        'session_duration': np.random.normal(10, 5, n).astype(int),  # Short sessions?
        'failed_logins': np.random.choice([0, 1, 2, 3], p=[0.1, 0.2, 0.3, 0.4], size=n),
        'sensitive_access': np.random.randint(2, 10, size=n)  # Accessing sensitive data
    }
    
    df = pd.DataFrame(data)
    df['login_hour'] = df['login_hour'].clip(0, 23)
    df['actions_count'] = df['actions_count'].clip(20, 100)
    df['files_accessed'] = df['files_accessed'].clip(5, 50)
    df['session_duration'] = df['session_duration'].clip(1, 60)
    
    return df

def train_and_save():
    print("Generating training data...")
    normal_df = generate_normal_data(4500)
    anomaly_df = generate_anomaly_data(500)
    
    # Combine datasets
    train_df = pd.concat([normal_df, anomaly_df], ignore_index=True)
    
    print(f"Training data shape: {train_df.shape}")
    print("Normal samples: 4500")
    print("Anomaly samples: 500")
    
    # Train Isolation Forest
    # contamination=0.1 means we expect about 10% anomalies in the training set
    print("Training Isolation Forest model...")
    clf = IsolationForest(
        n_estimators=100,
        max_samples='auto',
        contamination=0.1,
        random_state=42,
        n_jobs=-1
    )
    
    clf.fit(train_df)
    
    # Evaluate
    normal_preds = clf.predict(normal_df)
    anomaly_preds = clf.predict(anomaly_df)
    
    # 1 is normal, -1 is anomaly
    normal_acc = np.mean(normal_preds == 1)
    anomaly_acc = np.mean(anomaly_preds == -1)
    
    print(f"Accuracy on normal data: {normal_acc:.2%}")
    print(f"Accuracy on anomaly data: {anomaly_acc:.2%}")
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save()
