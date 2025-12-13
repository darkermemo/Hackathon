"""
Nafath SSO MVP - Extended API Server
=====================================
Flask REST API with full dashboard support.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from database import (
    init_database, seed_data, 
    get_all_users, get_user_by_id, get_user_by_national_id, create_user, get_users_by_tenant,
    get_all_roles, get_roles_by_tenant,
    get_activity_logs, get_alerts, get_dashboard_stats, get_user_sessions,
    get_all_tenants, get_tenant_by_id, get_tenant_by_code,
    get_tenant_integrations, update_integration,
    get_tenant_settings, update_tenant_settings,
    get_login_stats, get_platform_revenue,
    update_user_last_login
)
from auth import (
    initiate_nafath_auth, verify_nafath_otp, logout,
    require_auth, verify_jwt_token
)
from uba_service import (
    analyze_behavior, analyze_login, get_user_risk_profile
)
import os

# Get parent directory for static files
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask app with static files from parent directory
app = Flask(__name__, 
            static_folder=PARENT_DIR,
            static_url_path='/static')
CORS(app)

# =====================================
# HEALTH & INFO
# =====================================

@app.route('/')
def index():
    """Root route - API info"""
    return jsonify({
        'name': 'Nafath SSO MVP API',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'tenants': '/api/tenants',
            'users': '/api/users',
            'dashboard': '/api/dashboard/stats',
            'uba': '/api/uba/score'
        },
        'html_pages': {
            'dashboard': '/dashboard',
            'tenant_dashboard': '/tenant-dashboard',
            'uba_demo': '/uba-demo',
            'main_demo': '/demo'
        },
        'documentation': 'Use /api/health to check status'
    })

@app.route('/dashboard')
def serve_dashboard():
    """Serve SaaS Dashboard"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'dashboard.html')

@app.route('/tenant-dashboard')
def serve_tenant_dashboard():
    """Serve Tenant Dashboard"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'tenant-dashboard.html')

@app.route('/uba-demo')
def serve_uba_demo():
    """Serve UBA Demo"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'uba-demo.html')

@app.route('/demo')
def serve_main_demo():
    """Serve Main Demo"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'index.html')

@app.route('/styles.css')
def serve_styles():
    """Serve CSS"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'styles.css')

@app.route('/script.js')
def serve_script():
    """Serve JS"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'script.js')

@app.route('/slides')
def serve_slides():
    """Serve HLD Slides"""
    from flask import send_from_directory
    return send_from_directory(PARENT_DIR, 'slides.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Nafath SSO MVP',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def info():
    """System information"""
    return jsonify({
        'name': 'Nafath SSO MVP',
        'version': '2.0.0',
        'features': [
            'Multi-Tenant Architecture',
            'Nafath Authentication',
            'JWT Session Management',
            'Role-Based Access Control (RBAC)',
            'User Behavior Analytics (UBA)',
            'Activity Logging',
            'Security Alerts',
            'Integration Management'
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
        # Update last login
        user = get_user_by_national_id(national_id)
        update_user_last_login(user['id'])
        
        # Analyze login behavior with UBA
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
                'permissions': permissions,
                'tenant_code': user.get('tenant_code'),
                'tenant_name': user.get('tenant_name')
            }
        }), 200
    return jsonify({'success': False, 'error': 'User not found'}), 404

# =====================================
# TENANTS (ENTITIES)
# =====================================

@app.route('/api/tenants', methods=['GET'])
def list_tenants():
    """Get all tenants with stats"""
    tenants = get_all_tenants()
    revenue = get_platform_revenue()
    
    return jsonify({
        'success': True,
        'count': len(tenants),
        'total_revenue': revenue,
        'tenants': tenants
    }), 200

@app.route('/api/tenants/<int:tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    """Get tenant details"""
    tenant = get_tenant_by_id(tenant_id)
    if tenant:
        tenant['settings'] = get_tenant_settings(tenant_id)
        tenant['integrations'] = get_tenant_integrations(tenant_id)
        return jsonify({'success': True, 'tenant': tenant}), 200
    return jsonify({'success': False, 'error': 'Tenant not found'}), 404

@app.route('/api/tenants/code/<code>', methods=['GET'])
def get_tenant_by_code_endpoint(code):
    """Get tenant by code"""
    tenant = get_tenant_by_code(code)
    if tenant:
        return jsonify({'success': True, 'tenant': tenant}), 200
    return jsonify({'success': False, 'error': 'Tenant not found'}), 404

@app.route('/api/tenants/<int:tenant_id>/users', methods=['GET'])
def get_tenant_users(tenant_id):
    """Get all users for a tenant"""
    users = get_users_by_tenant(tenant_id)
    return jsonify({
        'success': True,
        'count': len(users),
        'users': users
    }), 200

@app.route('/api/tenants/<int:tenant_id>/roles', methods=['GET'])
def get_tenant_roles(tenant_id):
    """Get all roles for a tenant"""
    roles = get_roles_by_tenant(tenant_id)
    return jsonify({
        'success': True,
        'roles': roles
    }), 200

@app.route('/api/tenants/<int:tenant_id>/stats', methods=['GET'])
def get_tenant_stats(tenant_id):
    """Get tenant dashboard stats"""
    stats = get_dashboard_stats(tenant_id)
    login_stats = get_login_stats(tenant_id, days=7)
    
    return jsonify({
        'success': True,
        'stats': stats,
        'login_history': login_stats
    }), 200

@app.route('/api/tenants/<int:tenant_id>/logs', methods=['GET'])
def get_tenant_logs(tenant_id):
    """Get activity logs for a tenant"""
    limit = request.args.get('limit', 50, type=int)
    logs = get_activity_logs(tenant_id=tenant_id, limit=limit)
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs
    }), 200

@app.route('/api/tenants/<int:tenant_id>/alerts', methods=['GET'])
def get_tenant_alerts(tenant_id):
    """Get security alerts for a tenant"""
    is_resolved = request.args.get('resolved', type=lambda x: x.lower() == 'true')
    alerts = get_alerts(tenant_id=tenant_id, is_resolved=is_resolved)
    return jsonify({
        'success': True,
        'count': len(alerts),
        'alerts': alerts
    }), 200

# =====================================
# INTEGRATIONS
# =====================================

@app.route('/api/tenants/<int:tenant_id>/integrations', methods=['GET'])
def list_integrations(tenant_id):
    """Get all integrations for a tenant"""
    integrations = get_tenant_integrations(tenant_id)
    return jsonify({
        'success': True,
        'integrations': integrations
    }), 200

@app.route('/api/integrations/<int:integration_id>', methods=['PUT'])
@require_auth
def toggle_integration(integration_id):
    """Enable/disable an integration"""
    data = request.get_json()
    is_connected = data.get('is_connected', False)
    config = data.get('config')
    
    update_integration(integration_id, is_connected, config)
    
    return jsonify({
        'success': True,
        'message': 'Integration updated'
    }), 200

# =====================================
# TENANT SETTINGS
# =====================================

@app.route('/api/tenants/<int:tenant_id>/settings', methods=['GET'])
def get_settings(tenant_id):
    """Get tenant settings"""
    settings = get_tenant_settings(tenant_id)
    return jsonify({
        'success': True,
        'settings': settings
    }), 200

@app.route('/api/tenants/<int:tenant_id>/settings', methods=['PUT'])
@require_auth
def update_settings(tenant_id):
    """Update tenant settings"""
    data = request.get_json()
    allowed_keys = [
        'nafath_sso_enabled', 'two_factor_required', 'audit_logging',
        'siem_alerts', 'mdr_enabled', 'session_timeout_minutes', 'max_failed_attempts'
    ]
    settings = {k: v for k, v in data.items() if k in allowed_keys}
    
    update_tenant_settings(tenant_id, settings)
    
    return jsonify({
        'success': True,
        'message': 'Settings updated'
    }), 200

# =====================================
# USERS
# =====================================

@app.route('/api/users', methods=['GET'])
def list_users():
    """Get all users"""
    users = get_all_users()
    return jsonify({
        'success': True,
        'count': len(users),
        'users': users
    }), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if user:
        return jsonify({'success': True, 'user': user}), 200
    return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/api/users', methods=['POST'])
def add_user():
    """Create a new user"""
    data = request.get_json()
    
    required = ['tenant_id', 'national_id', 'name', 'role_id']
    for field in required:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'{field} is required'
            }), 400
    
    try:
        user_id = create_user(
            tenant_id=data['tenant_id'],
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
def list_roles():
    """Get all roles"""
    roles = get_all_roles()
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
    """Analyze user behavior"""
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
    
    result = analyze_behavior(user_id, session_data, data.get('action_data', {}))
    
    return jsonify({
        'success': True,
        'analysis': result
    }), 200

@app.route('/api/uba/profile/<int:user_id>', methods=['GET'])
def uba_profile(user_id):
    """Get user's risk profile"""
    profile = get_user_risk_profile(user_id)
    return jsonify({
        'success': True,
        'profile': profile
    }), 200

@app.route('/api/uba/score', methods=['POST'])
def uba_quick_score():
    """Quick UBA scoring (no auth required for demo)"""
    data = request.get_json()
    
    from uba_service import calculate_fallback_score, UBA_AVAILABLE
    
    behavior = {
        'login_hour': data.get('login_hour', 12),
        'location_id': data.get('location_id', 0),
        'is_new_device': data.get('is_new_device', False),
        'actions_count': data.get('actions_count', 1),
        'files_accessed': data.get('files_accessed', 0),
        'session_duration': data.get('session_duration', 0),
        'failed_logins': data.get('failed_logins', 0),
        'sensitive_access': data.get('sensitive_access', 0)
    }
    
    if UBA_AVAILABLE:
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'uba-model'))
            from uba_model import predict_risk_score
            result = predict_risk_score(behavior)
            risk_score = result['risk_score']
        except:
            risk_score = calculate_fallback_score(behavior)
    else:
        risk_score = calculate_fallback_score(behavior)
    
    if risk_score >= 60:
        status, status_ar = 'threat', 'تهديد محتمل'
    elif risk_score >= 30:
        status, status_ar = 'suspicious', 'سلوك مشبوه'
    else:
        status, status_ar = 'normal', 'سلوك طبيعي'
    
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
def list_logs():
    """Get activity logs"""
    user_id = request.args.get('user_id', type=int)
    tenant_id = request.args.get('tenant_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    logs = get_activity_logs(user_id=user_id, tenant_id=tenant_id, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs
    }), 200

# =====================================
# SECURITY ALERTS
# =====================================

@app.route('/api/alerts', methods=['GET'])
def list_alerts():
    """Get security alerts"""
    tenant_id = request.args.get('tenant_id', type=int)
    is_resolved = request.args.get('resolved', type=lambda x: x.lower() == 'true')
    limit = request.args.get('limit', 50, type=int)
    
    alerts = get_alerts(tenant_id=tenant_id, is_resolved=is_resolved, limit=limit)
    
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
# DASHBOARD - PLATFORM WIDE
# =====================================

@app.route('/api/dashboard/stats', methods=['GET'])
def platform_dashboard_stats():
    """Get platform-wide dashboard statistics"""
    stats = get_dashboard_stats()
    stats['total_revenue'] = get_platform_revenue()
    login_stats = get_login_stats(days=7)
    
    return jsonify({
        'success': True,
        'stats': stats,
        'login_history': login_stats
    }), 200

@app.route('/api/dashboard/revenue', methods=['GET'])
def get_revenue():
    """Get platform revenue"""
    revenue = get_platform_revenue()
    return jsonify({
        'success': True,
        'total_revenue': revenue,
        'currency': 'SAR'
    }), 200

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':
    print("=" * 60)
    print("  Nafath SSO MVP - Extended API Server v2.0")
    print("=" * 60)
    
    print("\n[1] Initializing database...")
    init_database()
    seed_data()
    
    print("\n[2] Starting Flask server on port 5002...")
    print("\n" + "-" * 60)
    print(" API Endpoints:")
    print("-" * 60)
    print("\n Auth:")
    print("   POST /api/auth/login     - Initiate Nafath auth")
    print("   POST /api/auth/verify    - Verify OTP & get token")
    print("   POST /api/auth/logout    - End session")
    print("   GET  /api/auth/me        - Get current user")
    print("\n Tenants:")
    print("   GET  /api/tenants                    - List all tenants")
    print("   GET  /api/tenants/<id>               - Get tenant details")
    print("   GET  /api/tenants/<id>/users         - Get tenant users")
    print("   GET  /api/tenants/<id>/stats         - Get tenant stats")
    print("   GET  /api/tenants/<id>/integrations  - Get integrations")
    print("   GET  /api/tenants/<id>/settings      - Get settings")
    print("   PUT  /api/tenants/<id>/settings      - Update settings")
    print("\n UBA:")
    print("   POST /api/uba/score      - Quick risk score")
    print("   POST /api/uba/analyze    - Full analysis")
    print("   GET  /api/uba/profile/<user_id> - User risk profile")
    print("\n Dashboard:")
    print("   GET  /api/dashboard/stats    - Platform stats")
    print("   GET  /api/dashboard/revenue  - Total revenue")
    print("\n" + "=" * 60)
    
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
