"""
Nafath SSO MVP - Main API Server
=================================
Flask REST API for the complete SSO system.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from database import (
    init_database, seed_data, get_all_users, get_user_by_id,
    get_user_by_national_id, create_user, get_all_roles,
    get_activity_logs, get_alerts, get_dashboard_stats,
    get_user_sessions
)
from auth import (
    initiate_nafath_auth, verify_nafath_otp, logout,
    require_auth, verify_jwt_token
)
from uba_service import (
    analyze_behavior, analyze_login, get_user_risk_profile
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# =====================================
# HEALTH & INFO
# =====================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Nafath SSO MVP',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def info():
    """System information"""
    return jsonify({
        'name': 'Nafath SSO MVP',
        'version': '1.0.0',
        'features': [
            'Nafath Authentication',
            'JWT Session Management',
            'Role-Based Access Control (RBAC)',
            'User Behavior Analytics (UBA)',
            'Activity Logging',
            'Security Alerts'
        ],
        'uba_model': 'Nafath-UBA-v2.1 (Isolation Forest)'
    })

# =====================================
# AUTHENTICATION
# =====================================

@app.route('/api/auth/login', methods=['POST'])
def login_step1():
    """
    Step 1: Initiate Nafath authentication
    Body: { "national_id": "1055443322" }
    """
    data = request.get_json()
    national_id = data.get('national_id')
    
    if not national_id:
        return jsonify({
            'success': False,
            'error': 'national_id required',
            'error_ar': 'يجب إدخال رقم الهوية'
        }), 400
    
    result = initiate_nafath_auth(national_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/auth/verify', methods=['POST'])
def login_step2():
    """
    Step 2: Verify OTP and complete login
    Body: { "national_id": "1055443322", "otp": "45" }
    """
    data = request.get_json()
    national_id = data.get('national_id')
    otp = data.get('otp')
    device_info = data.get('device_info', 'unknown')
    location = data.get('location', 'الرياض')
    
    if not national_id or not otp:
        return jsonify({
            'success': False,
            'error': 'national_id and otp required',
            'error_ar': 'يجب إدخال رقم الهوية ورمز التحقق'
        }), 400
    
    result = verify_nafath_otp(
        national_id=national_id,
        otp=otp,
        device_info=device_info,
        ip_address=request.remote_addr,
        location=location
    )
    
    if result['success']:
        # Analyze login behavior with UBA
        user = get_user_by_national_id(national_id)
        uba_result = analyze_login(
            user_id=user['id'],
            session_id=result['session_id'],
            login_hour=datetime.now().hour,
            location=location,
            location_id=0 if location in ['الرياض', 'riyadh'] else 1,
            is_new_device='new' in device_info.lower() if device_info else False
        )
        
        result['uba_analysis'] = {
            'risk_score': uba_result['risk_score'],
            'status': uba_result['status'],
            'status_ar': uba_result['status_ar']
        }
        
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout_user():
    """Logout and end session"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = logout(token)
    return jsonify(result), 200

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user"""
    user = get_user_by_id(request.current_user['user_id'])
    if user:
        permissions = json.loads(user.get('permissions', '[]')) if user.get('permissions') else []
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'national_id': user['national_id'],
                'name': user['name'],
                'name_ar': user['name_ar'],
                'email': user['email'],
                'role': user['role_name'],
                'role_ar': user['role_name_ar'],
                'permissions': permissions
            }
        }), 200
    return jsonify({'success': False, 'error': 'User not found'}), 404

# =====================================
# USERS
# =====================================

@app.route('/api/users', methods=['GET'])
@require_auth
def list_users():
    """Get all users"""
    users = get_all_users()
    return jsonify({
        'success': True,
        'count': len(users),
        'users': users
    }), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if user:
        return jsonify({'success': True, 'user': user}), 200
    return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/api/users', methods=['POST'])
@require_auth
def add_user():
    """Create a new user"""
    data = request.get_json()
    
    required = ['national_id', 'name', 'role_id']
    for field in required:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'{field} is required'
            }), 400
    
    try:
        user_id = create_user(
            national_id=data['national_id'],
            name=data['name'],
            name_ar=data.get('name_ar', data['name']),
            email=data.get('email'),
            role_id=data['role_id']
        )
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# =====================================
# ROLES
# =====================================

@app.route('/api/roles', methods=['GET'])
@require_auth
def list_roles():
    """Get all roles"""
    roles = get_all_roles()
    # Parse permissions JSON
    for role in roles:
        role['permissions'] = json.loads(role['permissions']) if role.get('permissions') else []
    return jsonify({
        'success': True,
        'roles': roles
    }), 200

# =====================================
# UBA - User Behavior Analytics
# =====================================

@app.route('/api/uba/analyze', methods=['POST'])
@require_auth
def uba_analyze():
    """
    Analyze user behavior
    Body: { session data and action details }
    """
    data = request.get_json()
    user_id = request.current_user['user_id']
    session_id = request.current_session['id']
    
    session_data = {
        'session_id': session_id,
        'login_hour': data.get('login_hour', datetime.now().hour),
        'location_id': data.get('location_id', 0),
        'is_new_device': data.get('is_new_device', False),
        'actions_count': data.get('actions_count', 1),
        'files_accessed': data.get('files_accessed', 0),
        'session_duration': data.get('session_duration', 0),
        'failed_logins': data.get('failed_logins', 0),
        'sensitive_access': data.get('sensitive_access', 0)
    }
    
    action_data = data.get('action_data', {})
    
    result = analyze_behavior(user_id, session_data, action_data)
    
    return jsonify({
        'success': True,
        'analysis': result
    }), 200

@app.route('/api/uba/profile/<int:user_id>', methods=['GET'])
@require_auth
def uba_profile(user_id):
    """Get user's risk profile"""
    profile = get_user_risk_profile(user_id)
    return jsonify({
        'success': True,
        'profile': profile
    }), 200

@app.route('/api/uba/score', methods=['POST'])
def uba_quick_score():
    """
    Quick UBA scoring (no auth required for demo)
    Body: { behavior features }
    """
    data = request.get_json()
    
    # Use the UBA model directly
    from uba_service import analyze_behavior
    
    session_data = {
        'session_id': None,
        'login_hour': data.get('login_hour', 12),
        'location_id': data.get('location_id', 0),
        'is_new_device': data.get('is_new_device', False),
        'actions_count': data.get('actions_count', 1),
        'files_accessed': data.get('files_accessed', 0),
        'session_duration': data.get('session_duration', 0),
        'failed_logins': data.get('failed_logins', 0),
        'sensitive_access': data.get('sensitive_access', 0)
    }
    
    # Calculate risk without logging (no user_id)
    from uba_service import calculate_fallback_score, UBA_AVAILABLE
    if UBA_AVAILABLE:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'uba-model'))
            from uba_model import predict_risk_score
            result = predict_risk_score(session_data)
        except:
            result = {'risk_score': calculate_fallback_score(session_data), 'anomaly_score': 0}
    else:
        result = {'risk_score': calculate_fallback_score(session_data), 'anomaly_score': 0}
    
    risk_score = result['risk_score']
    
    if risk_score >= 60:
        status = 'threat'
        status_ar = 'تهديد محتمل'
    elif risk_score >= 30:
        status = 'suspicious'
        status_ar = 'سلوك مشبوه'
    else:
        status = 'normal'
        status_ar = 'سلوك طبيعي'
    
    return jsonify({
        'success': True,
        'risk_score': risk_score,
        'status': status,
        'status_ar': status_ar,
        'model': 'Nafath-UBA-v2.1'
    }), 200

# =====================================
# ACTIVITY LOGS
# =====================================

@app.route('/api/logs', methods=['GET'])
@require_auth
def list_logs():
    """Get activity logs"""
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    logs = get_activity_logs(user_id=user_id, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs
    }), 200

@app.route('/api/logs/my', methods=['GET'])
@require_auth
def my_logs():
    """Get current user's activity logs"""
    user_id = request.current_user['user_id']
    limit = request.args.get('limit', 20, type=int)
    
    logs = get_activity_logs(user_id=user_id, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs
    }), 200

# =====================================
# SECURITY ALERTS
# =====================================

@app.route('/api/alerts', methods=['GET'])
@require_auth
def list_alerts():
    """Get security alerts"""
    is_resolved = request.args.get('resolved', type=lambda x: x.lower() == 'true')
    limit = request.args.get('limit', 50, type=int)
    
    alerts = get_alerts(is_resolved=is_resolved, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(alerts),
        'alerts': alerts
    }), 200

# =====================================
# SESSIONS
# =====================================

@app.route('/api/sessions', methods=['GET'])
@require_auth
def list_sessions():
    """Get user's sessions"""
    user_id = request.current_user['user_id']
    limit = request.args.get('limit', 10, type=int)
    
    sessions = get_user_sessions(user_id=user_id, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(sessions),
        'sessions': sessions
    }), 200

# =====================================
# DASHBOARD
# =====================================

@app.route('/api/dashboard/stats', methods=['GET'])
@require_auth
def dashboard_stats():
    """Get dashboard statistics"""
    stats = get_dashboard_stats()
    return jsonify({
        'success': True,
        'stats': stats
    }), 200

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':
    # Initialize database
    print("=" * 50)
    print("  Nafath SSO MVP - API Server")
    print("=" * 50)
    
    print("\n[1] Initializing database...")
    init_database()
    seed_data()
    
    print("\n[2] Starting Flask server...")
    print("\nEndpoints:")
    print("  Auth:")
    print("    POST /api/auth/login   - Initiate Nafath auth")
    print("    POST /api/auth/verify  - Verify OTP")
    print("    POST /api/auth/logout  - Logout")
    print("    GET  /api/auth/me      - Get current user")
    print("  Users:")
    print("    GET  /api/users        - List users")
    print("    POST /api/users        - Create user")
    print("  UBA:")
    print("    POST /api/uba/analyze  - Analyze behavior")
    print("    POST /api/uba/score    - Quick risk score (no auth)")
    print("  Logs & Alerts:")
    print("    GET  /api/logs         - Activity logs")
    print("    GET  /api/alerts       - Security alerts")
    print("\n" + "=" * 50)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
