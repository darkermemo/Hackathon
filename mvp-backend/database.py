"""
Database Layer - SQLite Setup
=============================
Handles all database operations for the Nafath SSO MVP.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = 'nafath_sso.db'

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with all tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_ar TEXT NOT NULL,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                national_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                name_ar TEXT,
                email TEXT,
                role_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                ip_address TEXT,
                device_info TEXT,
                location TEXT,
                location_id INTEGER DEFAULT 0,
                is_new_device BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                risk_score INTEGER DEFAULT 0,
                is_anomaly BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Create security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id INTEGER,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                is_resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        print("✓ Database tables created successfully")

def seed_data():
    """Seed database with demo data"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Seed roles
        roles = [
            ('diplomat', 'دبلوماسي', json.dumps([
                'view_classified', 'send_diplomatic_messages', 'access_embassy_data',
                'view_reports', 'manage_contacts', 'approve_requests'
            ])),
            ('admin_staff', 'موظف إداري', json.dumps([
                'view_reports', 'manage_users', 'view_logs', 'manage_documents'
            ])),
            ('consultant', 'مستشار', json.dumps([
                'view_reports', 'submit_recommendations'
            ])),
            ('guest', 'زائر', json.dumps([
                'view_public_info'
            ]))
        ]
        
        for name, name_ar, permissions in roles:
            cursor.execute('''
                INSERT OR IGNORE INTO roles (name, name_ar, permissions)
                VALUES (?, ?, ?)
            ''', (name, name_ar, permissions))
        
        # Seed users
        users = [
            ('1055443322', 'Ahmad Al-Diplomat', 'أحمد الدبلوماسي', 'ahmad@mofa.gov.sa', 1),
            ('1088776655', 'Fatima Al-Admin', 'فاطمة الإدارية', 'fatima@mofa.gov.sa', 2),
            ('1099887766', 'Khaled Al-Consultant', 'خالد المستشار', 'khaled@mofa.gov.sa', 3),
        ]
        
        for national_id, name, name_ar, email, role_id in users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (national_id, name, name_ar, email, role_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (national_id, name, name_ar, email, role_id))
        
        conn.commit()
        print("✓ Demo data seeded successfully")

# =====================================
# CRUD OPERATIONS
# =====================================

# Users
def get_user_by_national_id(national_id):
    """Get user by national ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar, r.permissions
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.national_id = ?
        ''', (national_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar, r.permissions
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_all_users():
    """Get all users"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def create_user(national_id, name, name_ar, email, role_id):
    """Create a new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (national_id, name, name_ar, email, role_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (national_id, name, name_ar, email, role_id))
        conn.commit()
        return cursor.lastrowid

# Sessions
def create_session(user_id, token, ip_address, device_info, location, location_id=0, is_new_device=False):
    """Create a new session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (user_id, token, ip_address, device_info, location, location_id, is_new_device)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, token, ip_address, device_info, location, location_id, is_new_device))
        conn.commit()
        return cursor.lastrowid

def get_session_by_token(token):
    """Get session by token"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE token = ? AND is_active = 1', (token,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def end_session(token):
    """End a session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions SET is_active = 0, logout_time = CURRENT_TIMESTAMP
            WHERE token = ?
        ''', (token,))
        conn.commit()

def get_user_sessions(user_id, limit=10):
    """Get user's recent sessions"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sessions WHERE user_id = ?
            ORDER BY login_time DESC LIMIT ?
        ''', (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]

# Activity Logs
def log_activity(user_id, session_id, action, details=None, risk_score=0, is_anomaly=False):
    """Log user activity"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_logs (user_id, session_id, action, details, risk_score, is_anomaly)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, action, json.dumps(details) if details else None, risk_score, is_anomaly))
        conn.commit()
        return cursor.lastrowid

def get_activity_logs(user_id=None, limit=50):
    """Get activity logs"""
    with get_db() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute('''
                SELECT al.*, u.name, u.national_id
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.user_id = ?
                ORDER BY al.timestamp DESC LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT al.*, u.name, u.national_id
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.timestamp DESC LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

# Security Alerts
def create_alert(user_id, session_id, alert_type, severity, description):
    """Create a security alert"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO security_alerts (user_id, session_id, alert_type, severity, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, alert_type, severity, description))
        conn.commit()
        return cursor.lastrowid

def get_alerts(is_resolved=None, limit=50):
    """Get security alerts"""
    with get_db() as conn:
        cursor = conn.cursor()
        if is_resolved is not None:
            cursor.execute('''
                SELECT sa.*, u.name, u.national_id
                FROM security_alerts sa
                LEFT JOIN users u ON sa.user_id = u.id
                WHERE sa.is_resolved = ?
                ORDER BY sa.created_at DESC LIMIT ?
            ''', (is_resolved, limit))
        else:
            cursor.execute('''
                SELECT sa.*, u.name, u.national_id
                FROM security_alerts sa
                LEFT JOIN users u ON sa.user_id = u.id
                ORDER BY sa.created_at DESC LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

# Roles
def get_all_roles():
    """Get all roles"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles')
        return [dict(row) for row in cursor.fetchall()]

# Stats
def get_dashboard_stats():
    """Get dashboard statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        total_users = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_active = 1')
        active_sessions = cursor.fetchone()[0]
        
        # Today's logins
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE date(login_time) = date('now')
        ''')
        today_logins = cursor.fetchone()[0]
        
        # Blocked attempts (high risk)
        cursor.execute('''
            SELECT COUNT(*) FROM activity_logs 
            WHERE is_anomaly = 1 AND date(timestamp) = date('now')
        ''')
        blocked_attempts = cursor.fetchone()[0]
        
        # Unresolved alerts
        cursor.execute('SELECT COUNT(*) FROM security_alerts WHERE is_resolved = 0')
        pending_alerts = cursor.fetchone()[0]
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'today_logins': today_logins,
            'blocked_attempts': blocked_attempts,
            'pending_alerts': pending_alerts
        }


if __name__ == '__main__':
    print("Initializing Nafath SSO Database...")
    init_database()
    seed_data()
    
    # Test
    print("\nTest: Get user by national ID")
    user = get_user_by_national_id('1055443322')
    print(f"  Found: {user['name_ar']} ({user['role_name_ar']})")
    
    print("\nDatabase ready!")
