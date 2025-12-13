"""
UBA Service Integration
=======================
Integrates the ML-based User Behavior Analytics with the backend.
"""

import sys
import os
import json
from datetime import datetime

# Add UBA model path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'uba-model'))

try:
    from uba_model import predict_risk_score, load_model
    UBA_AVAILABLE = True
except ImportError:
    UBA_AVAILABLE = False
    print("Warning: UBA model not available. Using fallback scoring.")

from database import log_activity, create_alert, get_user_sessions, get_activity_logs

# Risk thresholds
RISK_LOW = 30
RISK_MEDIUM = 60
RISK_HIGH = 80

def analyze_behavior(user_id, session_data, action_data=None):
    """
    Analyze user behavior and return risk score.
    
    Args:
        user_id: User ID
        session_data: Dict with session info (login_hour, location, device, etc.)
        action_data: Optional dict with current action details
    
    Returns:
        Dict with risk_score, status, and recommendations
    """
    # Prepare features for the model
    behavior = {
        'login_hour': session_data.get('login_hour', datetime.now().hour),
        'location_id': session_data.get('location_id', 0),
        'is_new_device': 1 if session_data.get('is_new_device', False) else 0,
        'actions_count': session_data.get('actions_count', 1),
        'files_accessed': session_data.get('files_accessed', 0),
        'session_duration': session_data.get('session_duration', 0),
        'failed_logins': session_data.get('failed_logins', 0),
        'sensitive_access': session_data.get('sensitive_access', 0)
    }
    
    # Get risk score from ML model
    if UBA_AVAILABLE:
        try:
            result = predict_risk_score(behavior)
            risk_score = result['risk_score']
            anomaly_score = result['anomaly_score']
        except Exception as e:
            print(f"UBA model error: {e}")
            risk_score = calculate_fallback_score(behavior)
            anomaly_score = 0
    else:
        risk_score = calculate_fallback_score(behavior)
        anomaly_score = 0
    
    # Determine status and actions
    is_anomaly = risk_score >= RISK_MEDIUM
    status = 'normal'
    status_ar = 'سلوك طبيعي'
    alert_action = None
    
    if risk_score >= RISK_HIGH:
        status = 'threat'
        status_ar = 'تهديد محتمل'
        alert_action = 'block_and_alert'
    elif risk_score >= RISK_MEDIUM:
        status = 'suspicious'
        status_ar = 'سلوك مشبوه'
        alert_action = 'monitor'
    
    # Log to database
    session_id = session_data.get('session_id')
    action = action_data.get('action', 'behavior_check') if action_data else 'behavior_check'
    
    log_id = log_activity(
        user_id=user_id,
        session_id=session_id,
        action=action,
        details={
            'behavior': behavior,
            'risk_score': risk_score,
            'status': status
        },
        risk_score=risk_score,
        is_anomaly=is_anomaly
    )
    
    # Create security alert if needed
    alert_id = None
    if risk_score >= RISK_HIGH:
        alert_id = create_alert(
            user_id=user_id,
            session_id=session_id,
            alert_type='high_risk_behavior',
            severity='critical',
            description=f'Risk score: {risk_score}. Behavior flagged as potentially malicious.'
        )
    elif risk_score >= RISK_MEDIUM:
        alert_id = create_alert(
            user_id=user_id,
            session_id=session_id,
            alert_type='suspicious_behavior',
            severity='warning',
            description=f'Risk score: {risk_score}. Investigating unusual behavior.'
        )
    
    return {
        'risk_score': risk_score,
        'anomaly_score': anomaly_score,
        'status': status,
        'status_ar': status_ar,
        'is_anomaly': is_anomaly,
        'action': alert_action,
        'log_id': log_id,
        'alert_id': alert_id,
        'features_analyzed': behavior,
        'model': 'Nafath-UBA-v2.1' if UBA_AVAILABLE else 'Fallback'
    }

def calculate_fallback_score(behavior):
    """
    Fallback scoring when ML model is not available.
    Simple rule-based scoring.
    """
    score = 0
    
    # Login hour (unusual if outside 6-20)
    hour = behavior.get('login_hour', 12)
    if hour < 6 or hour > 20:
        score += 25
    elif hour < 8 or hour > 18:
        score += 10
    
    # Location (3+ is unknown)
    if behavior.get('location_id', 0) >= 3:
        score += 30
    
    # New device
    if behavior.get('is_new_device', 0):
        score += 15
    
    # High action count
    actions = behavior.get('actions_count', 0)
    if actions > 50:
        score += 20
    elif actions > 30:
        score += 10
    
    # Files accessed
    files = behavior.get('files_accessed', 0)
    if files > 20:
        score += 20
    elif files > 10:
        score += 10
    
    # Failed logins
    failed = behavior.get('failed_logins', 0)
    if failed >= 3:
        score += 25
    elif failed >= 1:
        score += 10
    
    # Sensitive access
    sensitive = behavior.get('sensitive_access', 0)
    if sensitive >= 5:
        score += 20
    elif sensitive >= 3:
        score += 10
    
    return min(100, score)

def get_user_risk_profile(user_id):
    """
    Get user's risk profile based on historical behavior.
    """
    # Get recent sessions
    sessions = get_user_sessions(user_id, limit=20)
    
    # Get recent activity logs
    logs = get_activity_logs(user_id=user_id, limit=50)
    
    # Calculate stats
    total_sessions = len(sessions)
    anomaly_count = sum(1 for log in logs if log.get('is_anomaly'))
    avg_risk_score = sum(log.get('risk_score', 0) for log in logs) / max(len(logs), 1)
    
    # Determine profile
    if avg_risk_score >= 50 or anomaly_count >= 5:
        profile = 'high_risk'
        profile_ar = 'مخاطر عالية'
    elif avg_risk_score >= 30 or anomaly_count >= 2:
        profile = 'elevated'
        profile_ar = 'مخاطر مرتفعة'
    else:
        profile = 'normal'
        profile_ar = 'طبيعي'
    
    return {
        'user_id': user_id,
        'profile': profile,
        'profile_ar': profile_ar,
        'total_sessions': total_sessions,
        'anomaly_count': anomaly_count,
        'avg_risk_score': round(avg_risk_score, 1),
        'recent_logs_count': len(logs)
    }

def analyze_login(user_id, session_id, login_hour, location, location_id, is_new_device, failed_attempts=0):
    """
    Analyze login behavior specifically.
    Called when user logs in.
    """
    session_data = {
        'session_id': session_id,
        'login_hour': login_hour,
        'location_id': location_id,
        'is_new_device': is_new_device,
        'actions_count': 1,
        'files_accessed': 0,
        'session_duration': 0,
        'failed_logins': failed_attempts,
        'sensitive_access': 0
    }
    
    action_data = {
        'action': 'login',
        'location': location
    }
    
    return analyze_behavior(user_id, session_data, action_data)
