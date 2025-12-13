"""
Flask API Server for UBA Model
==============================
Provides REST API endpoints for the UBA ML model.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from uba_model import predict_risk_score, train_model, load_model
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Check if model exists, if not train it
if not os.path.exists('uba_model.pkl'):
    print("Model not found. Training new model...")
    train_model()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "Nafath-UBA-v2.1",
        "algorithm": "Isolation Forest"
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict risk score for user behavior.
    
    Expected JSON body:
    {
        "login_hour": 9,
        "location_id": 0,
        "is_new_device": 0,
        "actions_count": 15,
        "files_accessed": 5,
        "session_duration": 60,
        "failed_logins": 0,
        "sensitive_access": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result = predict_risk_score(data)
        
        return jsonify({
            "success": True,
            "model": "Nafath-UBA-v2.1",
            "result": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/analyze-session', methods=['POST'])
def analyze_session():
    """
    Analyze a user session with multiple activities.
    
    Expected JSON body:
    {
        "user_id": "1055443322",
        "session_id": "sess_123",
        "activities": [
            {"action": "login", "timestamp": "...", "details": {...}},
            {"action": "file_access", "timestamp": "...", "details": {...}},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Extract features from session
        activities = data.get('activities', [])
        
        # Calculate behavioral features
        login_hour = 12  # Default
        for act in activities:
            if act.get('action') == 'login':
                login_hour = act.get('details', {}).get('hour', 12)
                break
        
        behavior = {
            'login_hour': login_hour,
            'location_id': data.get('location_id', 0),
            'is_new_device': data.get('is_new_device', 0),
            'actions_count': len(activities),
            'files_accessed': sum(1 for a in activities if a.get('action') == 'file_access'),
            'session_duration': data.get('duration', 60),
            'failed_logins': data.get('failed_logins', 0),
            'sensitive_access': sum(1 for a in activities if a.get('details', {}).get('sensitive', False))
        }
        
        result = predict_risk_score(behavior)
        
        return jsonify({
            "success": True,
            "user_id": data.get('user_id'),
            "session_id": data.get('session_id'),
            "features_analyzed": behavior,
            "result": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Nafath UBA API Server")
    print("  Model: Nafath-UBA-v2.1 (Isolation Forest)")
    print("=" * 50)
    print("\nEndpoints:")
    print("  GET  /api/health   - Health check")
    print("  POST /api/predict  - Predict risk score")
    print("  POST /api/analyze-session - Analyze full session")
    print("\n" + "=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
