"""
Authentication Service
======================
Handles Nafath authentication simulation, JWT tokens, and session management.
"""

import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

from database import (
    get_user_by_national_id, create_session, get_session_by_token,
    end_session, log_activity
)

# Configuration
JWT_SECRET = 'nafath-sso-mvp-secret-key-2024'
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRY_HOURS = 8

# Simulated Nafath OTP storage (in production, this would be redis/memcached)
pending_otps = {}

def generate_otp():
    """Generate a 2-digit OTP (like Nafath app)"""
    return str(secrets.randbelow(90) + 10)

def generate_jwt_token(user_id, national_id, role):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'national_id': national_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token required', 'error_ar': 'يجب تسجيل الدخول'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token', 'error_ar': 'جلسة منتهية الصلاحية'}), 401
        
        # Check if session is still active
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Session ended', 'error_ar': 'تم إنهاء الجلسة'}), 401
        
        # Add user info to request
        request.current_user = payload
        request.current_session = session
        
        return f(*args, **kwargs)
    return decorated

def initiate_nafath_auth(national_id):
    """
    Step 1: Initiate Nafath authentication
    In real world: Would call Nafath API
    In MVP: Simulate OTP generation
    """
    # Check if user exists
    user = get_user_by_national_id(national_id)
    
    if not user:
        return {
            'success': False,
            'error': 'user_not_found',
            'error_ar': 'المستخدم غير مسجل في النظام'
        }
    
    if not user.get('is_active'):
        return {
            'success': False,
            'error': 'user_inactive',
            'error_ar': 'الحساب غير نشط'
        }
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP (expires in 2 minutes)
    pending_otps[national_id] = {
        'otp': otp,
        'user_id': user['id'],
        'expires': datetime.utcnow() + timedelta(minutes=2),
        'attempts': 0
    }
    
    return {
        'success': True,
        'message': 'OTP sent to Nafath app',
        'message_ar': 'تم إرسال رمز التحقق لتطبيق نفاذ',
        'otp_display': otp,  # In real world, this would NOT be returned
        'user_name': user['name_ar'],
        'expires_in': 120
    }

def verify_nafath_otp(national_id, otp, device_info=None, ip_address=None, location=None):
    """
    Step 2: Verify OTP and complete authentication
    """
    # Check if OTP exists
    if national_id not in pending_otps:
        return {
            'success': False,
            'error': 'no_pending_auth',
            'error_ar': 'لا توجد عملية مصادقة معلقة'
        }
    
    otp_data = pending_otps[national_id]
    
    # Check expiration
    if datetime.utcnow() > otp_data['expires']:
        del pending_otps[national_id]
        return {
            'success': False,
            'error': 'otp_expired',
            'error_ar': 'انتهت صلاحية رمز التحقق'
        }
    
    # Check attempts
    if otp_data['attempts'] >= 3:
        del pending_otps[national_id]
        return {
            'success': False,
            'error': 'max_attempts',
            'error_ar': 'تم تجاوز الحد الأقصى للمحاولات'
        }
    
    # Verify OTP
    if otp != otp_data['otp']:
        otp_data['attempts'] += 1
        return {
            'success': False,
            'error': 'invalid_otp',
            'error_ar': 'رمز التحقق غير صحيح',
            'attempts_remaining': 3 - otp_data['attempts']
        }
    
    # OTP verified - get user and create session
    user = get_user_by_national_id(national_id)
    
    # Generate JWT token
    token = generate_jwt_token(user['id'], national_id, user['role_name'])
    
    # Determine location ID (0-2 = known, 3+ = unknown)
    location_id = 0  # Default: Riyadh
    is_new_device = device_info and 'new' in str(device_info).lower()
    
    if location:
        known_locations = {'الرياض': 0, 'riyadh': 0, 'جدة': 1, 'jeddah': 1, 'الدمام': 2, 'dammam': 2}
        location_id = known_locations.get(location.lower(), 3)
    
    # Create session
    session_id = create_session(
        user_id=user['id'],
        token=token,
        ip_address=ip_address or request.remote_addr if request else 'unknown',
        device_info=device_info or 'unknown',
        location=location or 'الرياض',
        location_id=location_id,
        is_new_device=is_new_device
    )
    
    # Log activity
    log_activity(
        user_id=user['id'],
        session_id=session_id,
        action='login',
        details={
            'method': 'nafath',
            'location': location,
            'device': device_info
        }
    )
    
    # Clear OTP
    del pending_otps[national_id]
    
    # Import permissions
    import json
    permissions = json.loads(user.get('permissions', '[]')) if user.get('permissions') else []
    
    return {
        'success': True,
        'message': 'Authentication successful',
        'message_ar': 'تم التحقق بنجاح',
        'token': token,
        'session_id': session_id,
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
    }

def logout(token):
    """End user session"""
    session = get_session_by_token(token)
    if session:
        log_activity(
            user_id=session['user_id'],
            session_id=session['id'],
            action='logout',
            details={}
        )
        end_session(token)
        return {'success': True, 'message_ar': 'تم تسجيل الخروج'}
    return {'success': False, 'error_ar': 'جلسة غير موجودة'}
