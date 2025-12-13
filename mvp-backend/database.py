"""
Extended Database Layer
=======================
Adds tenants, contracts, integrations, and comprehensive stats.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
import random

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
        
        # Create tenants table (government entities)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                logo_emoji TEXT,
                color TEXT,
                contract_tier TEXT DEFAULT 'starter',
                contract_start DATE,
                contract_end DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                name TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                national_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                name_ar TEXT,
                email TEXT,
                role_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tenant_id INTEGER,
                token TEXT UNIQUE,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                ip_address TEXT,
                device_info TEXT,
                location TEXT,
                location_id INTEGER DEFAULT 0,
                is_new_device BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        # Create activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tenant_id INTEGER,
                session_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                risk_score INTEGER DEFAULT 0,
                is_anomaly BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Create security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tenant_id INTEGER,
                session_id INTEGER,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                is_resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        # Create integrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                name TEXT NOT NULL,
                name_ar TEXT,
                type TEXT NOT NULL,
                icon TEXT,
                color TEXT,
                is_connected BOOLEAN DEFAULT 0,
                config TEXT,
                last_sync TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        # Create tenant settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenant_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER UNIQUE,
                nafath_sso_enabled BOOLEAN DEFAULT 1,
                two_factor_required BOOLEAN DEFAULT 1,
                audit_logging BOOLEAN DEFAULT 1,
                siem_alerts BOOLEAN DEFAULT 1,
                mdr_enabled BOOLEAN DEFAULT 0,
                session_timeout_minutes INTEGER DEFAULT 480,
                max_failed_attempts INTEGER DEFAULT 3,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        # Create login stats table (for daily aggregation)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                date DATE NOT NULL,
                successful_logins INTEGER DEFAULT 0,
                failed_logins INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                blocked_attempts INTEGER DEFAULT 0,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        conn.commit()
        print("✓ Database tables created successfully")

def seed_data():
    """Seed database with comprehensive demo data"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Seed tenants (government entities)
        tenants = [
            ('MOFA', 'Ministry of Foreign Affairs', 'وزارة الخارجية', '🏛️', '#00965e', 'enterprise', '2024-01-01', '2025-12-31'),
            ('MOI', 'Ministry of Interior', 'وزارة الداخلية', '🛡️', '#1976d2', 'enterprise', '2024-03-01', '2024-09-30'),
            ('MOH', 'Ministry of Health', 'وزارة الصحة', '🏥', '#e65100', 'professional', '2024-02-01', '2025-01-31'),
            ('MOE', 'Ministry of Education', 'وزارة التعليم', '📚', '#7b1fa2', 'professional', '2024-11-01', '2024-12-15'),
            ('MOF', 'Ministry of Finance', 'وزارة المالية', '💼', '#00838f', 'starter', '2024-04-01', '2024-11-30'),
        ]
        
        for code, name, name_ar, emoji, color, tier, start, end in tenants:
            cursor.execute('''
                INSERT OR IGNORE INTO tenants (code, name, name_ar, logo_emoji, color, contract_tier, contract_start, contract_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, name_ar, emoji, color, tier, start, end))
        
        # Seed roles (per tenant)
        roles_data = [
            (1, 'diplomat', 'دبلوماسي', ['view_classified', 'send_diplomatic_messages', 'access_embassy_data', 'view_reports', 'manage_contacts', 'approve_requests']),
            (1, 'admin_staff', 'موظف إداري', ['view_reports', 'manage_users', 'view_logs', 'manage_documents']),
            (1, 'consultant', 'مستشار', ['view_reports', 'submit_recommendations']),
            (2, 'officer', 'ضابط', ['view_classified', 'manage_cases', 'view_reports']),
            (2, 'admin', 'إداري', ['view_reports', 'manage_users']),
            (3, 'doctor', 'طبيب', ['view_patient_records', 'manage_appointments']),
            (3, 'nurse', 'ممرض', ['view_patient_info', 'update_records']),
        ]
        
        for tenant_id, name, name_ar, permissions in roles_data:
            cursor.execute('''
                INSERT OR IGNORE INTO roles (tenant_id, name, name_ar, permissions)
                VALUES (?, ?, ?, ?)
            ''', (tenant_id, name, name_ar, json.dumps(permissions)))
        
        # Seed users (across tenants)
        users = [
            # MOFA users
            (1, '1055443322', 'Ahmad Al-Diplomat', 'أحمد الدبلوماسي', 'ahmad@mofa.gov.sa', 1),
            (1, '1088776655', 'Fatima Al-Admin', 'فاطمة الإدارية', 'fatima@mofa.gov.sa', 2),
            (1, '1099887766', 'Khaled Al-Consultant', 'خالد المستشار', 'khaled@mofa.gov.sa', 3),
            # MOI users
            (2, '1011223344', 'Mohammed Al-Officer', 'محمد الضابط', 'mohammed@moi.gov.sa', 4),
            (2, '1022334455', 'Sara Al-Admin', 'سارة الإدارية', 'sara@moi.gov.sa', 5),
            # MOH users
            (3, '1033445566', 'Dr. Ali Hassan', 'د. علي حسن', 'ali@moh.gov.sa', 6),
            (3, '1044556677', 'Noura Al-Nurse', 'نورة الممرضة', 'noura@moh.gov.sa', 7),
        ]
        
        for tenant_id, national_id, name, name_ar, email, role_id in users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (tenant_id, national_id, name, name_ar, email, role_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tenant_id, national_id, name, name_ar, email, role_id))
        
        # Seed integrations for each tenant
        integration_types = [
            ('Nafath SSO', 'نفاذ SSO', 'sso', 'fa-fingerprint', '#28a745', True),
            ('SIEM', 'SIEM', 'security', 'fa-database', '#1976d2', True),
            ('MDR Service', 'خدمة MDR', 'security', 'fa-shield-alt', '#c2185b', True),
            ('Email Alerts', 'تنبيهات البريد', 'notification', 'fa-envelope', '#e65100', False),
            ('SMS Alerts', 'تنبيهات SMS', 'notification', 'fa-mobile-alt', '#7b1fa2', False),
            ('Slack', 'Slack', 'notification', 'fa-slack', '#3f51b5', False),
        ]
        
        for tenant_id in range(1, 6):
            for name, name_ar, type_, icon, color, connected in integration_types:
                # Enterprise tenants get more integrations connected
                is_connected = connected if tenant_id <= 2 else (connected and name == 'Nafath SSO')
                cursor.execute('''
                    INSERT OR IGNORE INTO integrations (tenant_id, name, name_ar, type, icon, color, is_connected)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (tenant_id, name, name_ar, type_, icon, color, is_connected))
        
        # Seed tenant settings
        for tenant_id in range(1, 6):
            cursor.execute('''
                INSERT OR IGNORE INTO tenant_settings (tenant_id, nafath_sso_enabled, two_factor_required, audit_logging, siem_alerts, mdr_enabled)
                VALUES (?, 1, 1, 1, ?, ?)
            ''', (tenant_id, 1 if tenant_id <= 3 else 0, 1 if tenant_id <= 2 else 0))
        
        # Seed login stats for last 30 days
        today = datetime.now().date()
        for tenant_id in range(1, 6):
            base_logins = {1: 60, 2: 100, 3: 70, 4: 25, 5: 15}[tenant_id]
            for days_ago in range(30):
                date = today - timedelta(days=days_ago)
                # Weekend has fewer logins
                multiplier = 0.3 if date.weekday() >= 5 else 1.0
                successful = int(base_logins * multiplier * (0.8 + random.random() * 0.4))
                failed = int(successful * 0.02 * (0.5 + random.random()))
                blocked = int(failed * 0.5)
                cursor.execute('''
                    INSERT OR IGNORE INTO login_stats (tenant_id, date, successful_logins, failed_logins, unique_users, blocked_attempts)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (tenant_id, date.isoformat(), successful, failed, int(successful * 0.7), blocked))
        
        # Seed some activity logs
        actions = ['login', 'view_document', 'edit_document', 'send_message', 'view_report', 'export_data']
        for user_id in range(1, 8):
            for _ in range(random.randint(10, 30)):
                action = random.choice(actions)
                risk = random.randint(0, 25) if action != 'export_data' else random.randint(20, 50)
                is_anomaly = risk > 40
                cursor.execute('''
                    INSERT INTO activity_logs (user_id, tenant_id, action, risk_score, is_anomaly, timestamp)
                    VALUES (?, ?, ?, ?, ?, datetime('now', ?))
                ''', (user_id, (user_id - 1) // 3 + 1, action, risk, is_anomaly, f'-{random.randint(0, 720)} minutes'))
        
        # Seed some security alerts
        alert_types = [
            ('high_risk_behavior', 'critical', 'Unusual access pattern detected'),
            ('suspicious_behavior', 'warning', 'Multiple failed login attempts'),
            ('new_device_login', 'info', 'Login from new device'),
        ]
        for tenant_id in range(1, 4):
            for _ in range(random.randint(2, 5)):
                alert_type, severity, desc = random.choice(alert_types)
                cursor.execute('''
                    INSERT INTO security_alerts (tenant_id, alert_type, severity, description, is_resolved, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now', ?))
                ''', (tenant_id, alert_type, severity, desc, random.choice([0, 0, 1]), f'-{random.randint(0, 168)} hours'))
        
        conn.commit()
        print("✓ Demo data seeded successfully")

# =====================================
# TENANT OPERATIONS
# =====================================

def get_all_tenants():
    """Get all tenants with stats"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.*,
                   (SELECT COUNT(*) FROM users WHERE tenant_id = t.id AND is_active = 1) as user_count,
                   (SELECT SUM(successful_logins) FROM login_stats WHERE tenant_id = t.id AND date >= date('now', '-30 days')) as monthly_logins,
                   (SELECT SUM(failed_logins) FROM login_stats WHERE tenant_id = t.id AND date >= date('now', '-30 days')) as monthly_failures
            FROM tenants t
            WHERE t.is_active = 1
            ORDER BY t.id
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_tenant_by_id(tenant_id):
    """Get tenant by ID with full details"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.*,
                   (SELECT COUNT(*) FROM users WHERE tenant_id = t.id AND is_active = 1) as user_count,
                   (SELECT COUNT(*) FROM roles WHERE tenant_id = t.id) as role_count
            FROM tenants t
            WHERE t.id = ?
        ''', (tenant_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_tenant_by_code(code):
    """Get tenant by code"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tenants WHERE code = ?', (code,))
        row = cursor.fetchone()
        return dict(row) if row else None

# =====================================
# USER OPERATIONS
# =====================================

def get_user_by_national_id(national_id):
    """Get user by national ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar, r.permissions,
                   t.code as tenant_code, t.name_ar as tenant_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN tenants t ON u.tenant_id = t.id
            WHERE u.national_id = ?
        ''', (national_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar, r.permissions,
                   t.code as tenant_code, t.name_ar as tenant_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN tenants t ON u.tenant_id = t.id
            WHERE u.id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_users_by_tenant(tenant_id):
    """Get all users for a tenant"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.tenant_id = ?
            ORDER BY u.created_at DESC
        ''', (tenant_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_all_users():
    """Get all users"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.name_ar as role_name_ar,
                   t.code as tenant_code, t.name_ar as tenant_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN tenants t ON u.tenant_id = t.id
            ORDER BY u.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def create_user(tenant_id, national_id, name, name_ar, email, role_id):
    """Create a new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (tenant_id, national_id, name, name_ar, email, role_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tenant_id, national_id, name, name_ar, email, role_id))
        conn.commit()
        return cursor.lastrowid

def update_user_last_login(user_id):
    """Update user's last login time"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        conn.commit()

# =====================================
# SESSION OPERATIONS
# =====================================

def create_session(user_id, token, ip_address, device_info, location, location_id=0, is_new_device=False, tenant_id=None):
    """Create a new session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (user_id, tenant_id, token, ip_address, device_info, location, location_id, is_new_device)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, tenant_id, token, ip_address, device_info, location, location_id, is_new_device))
        conn.commit()
        return cursor.lastrowid

def get_session_by_token(token):
    """Get session by token"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE token = ? AND is_active = 1', (token,))
        row = cursor.fetchone()
        return dict(row) if row else None

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

# =====================================
# ACTIVITY & LOGS
# =====================================

def log_activity(user_id, session_id, action, details=None, risk_score=0, is_anomaly=False, tenant_id=None):
    """Log user activity"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_logs (user_id, tenant_id, session_id, action, details, risk_score, is_anomaly)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, tenant_id, session_id, action, json.dumps(details) if details else None, risk_score, is_anomaly))
        conn.commit()
        return cursor.lastrowid

def get_activity_logs(user_id=None, tenant_id=None, limit=50):
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
        elif tenant_id:
            cursor.execute('''
                SELECT al.*, u.name, u.national_id
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.tenant_id = ?
                ORDER BY al.timestamp DESC LIMIT ?
            ''', (tenant_id, limit))
        else:
            cursor.execute('''
                SELECT al.*, u.name, u.national_id
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.timestamp DESC LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

# =====================================
# SECURITY ALERTS
# =====================================

def create_alert(user_id, session_id, alert_type, severity, description, tenant_id=None):
    """Create a security alert"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO security_alerts (user_id, tenant_id, session_id, alert_type, severity, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, tenant_id, session_id, alert_type, severity, description))
        conn.commit()
        return cursor.lastrowid

def get_alerts(tenant_id=None, is_resolved=None, limit=50):
    """Get security alerts"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT sa.*, u.name, u.national_id, t.name_ar as tenant_name
            FROM security_alerts sa
            LEFT JOIN users u ON sa.user_id = u.id
            LEFT JOIN tenants t ON sa.tenant_id = t.id
        '''
        conditions = []
        params = []
        
        if tenant_id:
            conditions.append('sa.tenant_id = ?')
            params.append(tenant_id)
        if is_resolved is not None:
            conditions.append('sa.is_resolved = ?')
            params.append(is_resolved)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY sa.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

# =====================================
# INTEGRATIONS
# =====================================

def get_tenant_integrations(tenant_id):
    """Get all integrations for a tenant"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM integrations WHERE tenant_id = ?', (tenant_id,))
        return [dict(row) for row in cursor.fetchall()]

def update_integration(integration_id, is_connected, config=None):
    """Update integration status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE integrations SET is_connected = ?, config = ?, last_sync = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (is_connected, json.dumps(config) if config else None, integration_id))
        conn.commit()

# =====================================
# TENANT SETTINGS
# =====================================

def get_tenant_settings(tenant_id):
    """Get tenant settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tenant_settings WHERE tenant_id = ?', (tenant_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_tenant_settings(tenant_id, settings):
    """Update tenant settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        columns = ', '.join(f'{k} = ?' for k in settings.keys())
        values = list(settings.values()) + [tenant_id]
        cursor.execute(f'UPDATE tenant_settings SET {columns} WHERE tenant_id = ?', values)
        conn.commit()

# =====================================
# ROLES
# =====================================

def get_all_roles():
    """Get all roles"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles')
        roles = [dict(row) for row in cursor.fetchall()]
        for role in roles:
            role['permissions'] = json.loads(role['permissions']) if role.get('permissions') else []
        return roles

def get_roles_by_tenant(tenant_id):
    """Get roles for a tenant"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE tenant_id = ?', (tenant_id,))
        roles = [dict(row) for row in cursor.fetchall()]
        for role in roles:
            role['permissions'] = json.loads(role['permissions']) if role.get('permissions') else []
        return roles

# =====================================
# STATISTICS
# =====================================

def get_login_stats(tenant_id=None, days=7):
    """Get login statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        if tenant_id:
            cursor.execute('''
                SELECT date, successful_logins, failed_logins, blocked_attempts
                FROM login_stats
                WHERE tenant_id = ? AND date >= date('now', ?)
                ORDER BY date DESC
            ''', (tenant_id, f'-{days} days'))
        else:
            cursor.execute('''
                SELECT date, SUM(successful_logins) as successful_logins, 
                       SUM(failed_logins) as failed_logins,
                       SUM(blocked_attempts) as blocked_attempts
                FROM login_stats
                WHERE date >= date('now', ?)
                GROUP BY date
                ORDER BY date DESC
            ''', (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]

def get_dashboard_stats(tenant_id=None):
    """Get dashboard statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if tenant_id:
            # Tenant-specific stats
            cursor.execute('SELECT COUNT(*) FROM users WHERE tenant_id = ? AND is_active = 1', (tenant_id,))
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sessions WHERE tenant_id = ? AND is_active = 1', (tenant_id,))
            active_sessions = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COALESCE(SUM(successful_logins), 0) FROM login_stats 
                WHERE tenant_id = ? AND date >= date('now', '-30 days')
            ''', (tenant_id,))
            monthly_logins = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM activity_logs WHERE tenant_id = ? AND is_anomaly = 1
            ''', (tenant_id,))
            blocked_attempts = cursor.fetchone()[0]
        else:
            # Platform-wide stats
            cursor.execute('SELECT COUNT(*) FROM tenants WHERE is_active = 1')
            total_tenants = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_active = 1')
            active_sessions = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COALESCE(SUM(successful_logins), 0) FROM login_stats 
                WHERE date >= date('now', '-30 days')
            ''')
            monthly_logins = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM activity_logs WHERE is_anomaly = 1')
            blocked_attempts = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM security_alerts WHERE is_resolved = 0')
            pending_alerts = cursor.fetchone()[0]
            
            return {
                'total_tenants': total_tenants,
                'total_users': total_users,
                'active_sessions': active_sessions,
                'monthly_logins': monthly_logins,
                'blocked_attempts': blocked_attempts,
                'pending_alerts': pending_alerts
            }
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'monthly_logins': monthly_logins,
            'blocked_attempts': blocked_attempts
        }

def get_platform_revenue():
    """Calculate total platform revenue"""
    pricing = {'enterprise': 150000, 'professional': 75000, 'starter': 25000}
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT contract_tier, COUNT(*) as count FROM tenants WHERE is_active = 1 GROUP BY contract_tier')
        total = 0
        for row in cursor.fetchall():
            total += pricing.get(row['contract_tier'], 0) * row['count']
        return total


if __name__ == '__main__':
    print("Initializing Nafath SSO Database (Extended)...")
    init_database()
    seed_data()
    
    # Test
    print("\nTest: Get all tenants")
    tenants = get_all_tenants()
    for t in tenants:
        print(f"  - {t['name_ar']} ({t['code']}): {t['user_count']} users, {t['monthly_logins']} logins")
    
    print(f"\nTotal Revenue: {get_platform_revenue():,} SAR")
    print("\nDatabase ready!")
