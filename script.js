// MOFA Demo - Scenario-Based with Manual Controls & UBA
// Restructured for judge presentations

// ==========================================
// SCENARIO DEFINITIONS
// ==========================================

const SCENARIOS = {
    menu: {
        id: 'menu',
        name: 'القائمة الرئيسية',
        nameEn: 'Main Menu'
    },
    onboarding: {
        id: 'onboarding',
        name: 'الإعداد الأولي',
        nameEn: 'SDK Integration & Onboarding',
        icon: 'cogs',
        color: 'warning',
        description: 'إعداد SDK ونفاذ وتعيين الصلاحيات',
        steps: [
            { id: 'sdk-setup', name: 'إعداد SDK', screen: 'sdk-setup', action: 'showSDKSetup', duration: 3000 },
            { id: 'nafath-config', name: 'ربط نفاذ', screen: 'nafath-config', action: 'showNafathConfig', duration: 2500 },
            { id: 'rbac-admin', name: 'لوحة المسؤول', screen: 'rbac-admin', action: 'showRBACAdmin', duration: 3000 },
            { id: 'assign-permissions', name: 'تعيين الصلاحيات', screen: 'assign-permissions', action: 'showAssignPermissions', duration: 2500 },
            { id: 'test-auth', name: 'اختبار المصادقة', screen: 'test-auth', action: 'showTestAuth', duration: 2000 },
            { id: 'deployment', name: 'جاهز للإنتاج', screen: 'deployment-ready', action: 'showDeploymentReady', duration: 2000 }
        ]
    },
    normal: {
        id: 'normal',
        name: 'التدفق العادي',
        nameEn: 'Normal Authentication Flow',
        icon: 'user-check',
        color: 'success',
        description: 'مستخدم دبلوماسي بصلاحيات كاملة',
        steps: [
            { id: 'mofa-login', name: 'تسجيل الدخول', screen: 'mofa-login', duration: 2000 },
            { id: 'redirect', name: 'التحويل لنفاذ', screen: 'redirect', duration: 1500 },
            { id: 'credentials', name: 'بيانات الاعتماد', screen: 'sso-login', action: 'fillCredentials', duration: 2000 },
            { id: 'otp', name: 'رمز التحقق', screen: 'sso-login', action: 'showOTP', duration: 1500 },
            { id: 'device-verify', name: 'التحقق الأمني', screen: 'device-verify', action: 'verifyDevice', duration: 2000 },
            { id: 'session', name: 'إنشاء الجلسة', screen: 'session-create', duration: 1500 },
            { id: 'permissions', name: 'الصلاحيات المخولة', screen: 'user-permissions', action: 'showUserPermissions', duration: 2500 },
            { id: 'dashboard', name: 'لوحة التحكم', screen: 'mofa-dashboard', action: 'showDashboard', duration: 2000 },
            { id: 'access-module', name: 'الوصول للوحدة', screen: 'module-success', action: 'showModuleAccess', duration: 2000 }
        ]
    },
    unauthorized: {
        id: 'unauthorized',
        name: 'محاولة وصول غير مصرح',
        nameEn: 'Unauthorized Access Attempt',
        icon: 'ban',
        color: 'danger',
        description: 'مستخدم بصلاحيات محدودة يحاول الوصول لوحدة محظورة',
        steps: [
            { id: 'login-restricted', name: 'تسجيل دخول محدود', screen: 'mofa-login', action: 'selectRestrictedUser', duration: 2000 },
            { id: 'sso-quick', name: 'المصادقة السريعة', screen: 'sso-quick', action: 'quickAuth', duration: 1500 },
            { id: 'dashboard-locked', name: 'الوحدات المقفلة', screen: 'mofa-dashboard', action: 'showLockedModules', duration: 2000 },
            { id: 'attempt', name: 'محاولة الوصول', screen: 'access-attempt', action: 'attemptAccess', duration: 1500 },
            { id: 'denied', name: 'رفض الوصول', screen: 'access-denied', action: 'showAccessDenied', duration: 2000 },
            { id: 'soc-alert', name: 'تنبيه SOC', screen: 'soc-alert', action: 'triggerSOCAlert', duration: 2000 },
            { id: 'mdr', name: 'إرسال لـ SITE.sa', screen: 'mdr-integration', action: 'forwardToMDR', duration: 2000 },
            { id: 'logged', name: 'تسجيل الحدث', screen: 'event-logged', action: 'showEventLogged', duration: 1500 }
        ]
    },
    soc: {
        id: 'soc',
        name: 'لوحة فريق الأمن',
        nameEn: 'SOC Dashboard',
        icon: 'shield-alt',
        color: 'primary',
        description: 'مركز العمليات الأمنية - عرض شامل',
        steps: [
            { id: 'soc-overview', name: 'نظرة عامة', screen: 'soc-dashboard', action: 'showSOCDashboard', duration: 3000 }
        ]
    },
    uba: {
        id: 'uba',
        name: 'تحليل سلوك المستخدم',
        nameEn: 'User Behavior Analytics',
        icon: 'chart-line',
        color: 'info',
        description: 'الكشف عن الأنماط الشاذة والتهديدات الداخلية',
        steps: [
            { id: 'uba-overview', name: 'نظرة عامة', screen: 'uba-dashboard', action: 'showUBADashboard', duration: 3000 }
        ]
    },
    adcompromise: {
        id: 'adcompromise',
        name: 'حماية من اختراق AD',
        nameEn: 'AD Compromise Protection',
        icon: 'user-shield',
        color: 'security',
        description: 'البيانات محمية حتى لو تم اختراق Active Directory',
        steps: [
            { id: 'ad-breach', name: 'اختراق AD', screen: 'ad-breach', action: 'showADBreach', duration: 3000 },
            { id: 'attacker-attempt', name: 'محاولة الدخول', screen: 'attacker-attempt', action: 'showAttackerAttempt', duration: 2500 },
            { id: 'sso-required', name: 'نفاذ مطلوب', screen: 'sso-required', action: 'showSSORequired', duration: 2500 },
            { id: 'no-otp', name: 'لا يوجد OTP', screen: 'no-otp', action: 'showNoOTP', duration: 2500 },
            { id: 'access-blocked', name: 'تم الحظر', screen: 'access-blocked', action: 'showAccessBlocked', duration: 2500 },
            { id: 'data-safe', name: 'البيانات آمنة', screen: 'data-safe', action: 'showDataSafe', duration: 3000 }
        ]
    }
};

// User roles
const demoUsers = [
    {
        id: 'diplomat',
        name: 'أحمد الدبلوماسي',
        nameEn: 'Ahmad Al-Diplomat',
        nationalId: '1055443322',
        role: 'diplomat',
        roleAr: 'دبلوماسي',
        permissions: ['messaging', 'documents', 'cables', 'embassy', 'analytics', 'notifications'],
        badge: 'success',
        riskScore: 15
    },
    {
        id: 'admin-staff',
        name: 'فاطمة الإدارية',
        nameEn: 'Fatima Admin',
        nationalId: '1088776655',
        role: 'admin-staff',
        roleAr: 'موظف إداري',
        permissions: ['messaging', 'documents', 'notifications'],
        badge: 'warning',
        riskScore: 35
    },
    {
        id: 'consultant',
        name: 'خالد الاستشاري',
        nameEn: 'Khalid Consultant',
        nationalId: '2123456789',
        role: 'consultant',
        roleAr: 'مستشار خارجي',
        permissions: ['documents'],
        badge: 'danger',
        riskScore: 72
    }
];

const modules = [
    { id: 'messaging', nameAr: 'المراسلات الآمنة', icon: 'comments', color: 'messaging', badge: '24' },
    { id: 'documents', nameAr: 'إدارة الوثائق', icon: 'folder-open', color: 'documents', badge: '156' },
    { id: 'cables', nameAr: 'البرقيات الدبلوماسية', icon: 'broadcast-tower', color: 'cables', badge: '8' },
    { id: 'embassy', nameAr: 'شبكة السفارات', icon: 'globe-americas', color: 'embassy', badge: '42' },
    { id: 'analytics', nameAr: 'التقارير', icon: 'chart-line', color: 'analytics', badge: '∞' },
    { id: 'notifications', nameAr: 'الإشعارات', icon: 'bell', color: 'notifications', badge: '3' }
];

// ==========================================
// STATE MANAGEMENT
// ==========================================

let currentScenario = 'menu';
let currentStepIndex = 0;
let currentUser = demoUsers[0];
let isAutoPlay = false;
let securityEvents = [];

// ==========================================
// NAVIGATION FUNCTIONS
// ==========================================

function showScenarioMenu() {
    currentScenario = 'menu';
    currentStepIndex = 0;
    showScreen('scenario-menu');
    updateNavigationControls();
}

function startScenario(scenarioId) {
    currentScenario = scenarioId;
    currentStepIndex = 0;

    // Set user based on scenario
    if (scenarioId === 'normal') {
        currentUser = demoUsers[0]; // Diplomat
    } else if (scenarioId === 'unauthorized') {
        currentUser = demoUsers[2]; // Consultant (most restricted)
    }

    executeCurrentStep();
    updateNavigationControls();
}

function nextStep() {
    const scenario = SCENARIOS[currentScenario];
    if (!scenario || !scenario.steps) return;

    if (currentStepIndex < scenario.steps.length - 1) {
        currentStepIndex++;
        executeCurrentStep();
        updateNavigationControls();
    }
}

function previousStep() {
    if (currentStepIndex > 0) {
        currentStepIndex--;
        executeCurrentStep();
        updateNavigationControls();
    }
}

function executeCurrentStep() {
    const scenario = SCENARIOS[currentScenario];
    if (!scenario || !scenario.steps) return;

    const step = scenario.steps[currentStepIndex];
    if (!step) return;

    // Show screen
    showScreen(step.screen);

    // Execute action if defined
    if (step.action && window[step.action]) {
        setTimeout(() => {
            window[step.action]();
        }, 100);
    }

    // Auto-advance if enabled
    if (isAutoPlay && currentStepIndex < scenario.steps.length - 1) {
        setTimeout(() => {
            nextStep();
        }, step.duration || 2000);
    }
}

function toggleAutoPlay() {
    isAutoPlay = !isAutoPlay;
    const btn = document.getElementById('btn-autoplay');
    if (btn) {
        btn.innerHTML = isAutoPlay ?
            '<i class="fas fa-pause"></i> إيقاف' :
            '<i class="fas fa-play"></i> تشغيل تلقائي';
        btn.classList.toggle('active', isAutoPlay);
    }

    if (isAutoPlay) {
        executeCurrentStep(); // Restart with auto-play
    }
}

function updateNavigationControls() {
    const scenario = SCENARIOS[currentScenario];

    // Show/hide controls
    const controls = document.getElementById('navigation-controls');
    if (controls) {
        controls.style.display = currentScenario === 'menu' ? 'none' : 'flex';
    }

    if (currentScenario === 'menu') return;

    // Update buttons
    const prevBtn = document.getElementById('btn-prev');
    const nextBtn = document.getElementById('btn-next');

    if (prevBtn) {
        prevBtn.disabled = currentStepIndex === 0;
    }

    if (nextBtn && scenario.steps) {
        nextBtn.disabled = currentStepIndex >= scenario.steps.length - 1;
    }

    // Update progress
    const progressText = document.getElementById('progress-text');
    const progressBar = document.getElementById('progress-bar');
    const scenarioTitle = document.getElementById('scenario-title');

    if (scenario.steps) {
        if (progressText) {
            progressText.textContent = `الخطوة ${currentStepIndex + 1} من ${scenario.steps.length}`;
        }

        if (progressBar) {
            const progress = ((currentStepIndex + 1) / scenario.steps.length) * 100;
            progressBar.style.width = `${progress}%`;
        }

        if (scenarioTitle) {
            const step = scenario.steps[currentStepIndex];
            scenarioTitle.innerHTML = `<i class="fas fa-${scenario.icon}"></i> ${scenario.name}: ${step.name}`;
        }
    }
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => {
        s.classList.remove('active');
        s.style.display = 'none';
    });

    const target = document.getElementById(`screen-${screenId}`);
    if (target) {
        target.style.display = 'block';
        setTimeout(() => target.classList.add('active'), 50);
    }
}

// ==========================================
// STEP ACTION FUNCTIONS
// ==========================================

function selectRestrictedUser() {
    currentUser = demoUsers[2]; // Consultant
    const userCard = document.getElementById('current-user-card');
    if (userCard) {
        userCard.innerHTML = `
            <div class="user-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="user-info">
                <h4>${currentUser.name}</h4>
                <span class="role-badge role-${currentUser.badge}">${currentUser.roleAr}</span>
            </div>
        `;
    }
}

function fillCredentials() {
    setTimeout(() => {
        document.getElementById('sso-username').value = currentUser.nationalId;
        document.querySelectorAll('.form-group')[0]?.classList.add('filled');
    }, 300);

    setTimeout(() => {
        document.getElementById('sso-password').value = '••••••••';
        document.querySelectorAll('.form-group')[1]?.classList.add('filled');
    }, 600);
}

function showOTP() {
    document.getElementById('sso-step-1').style.display = 'none';
    document.getElementById('sso-otp-wrapper').style.display = 'block';

    setTimeout(() => {
        document.getElementById('sso-otp').value = '123456';
        document.querySelectorAll('.form-group')[2]?.classList.add('filled');
    }, 300);
}

function quickAuth() {
    // Show abbreviated auth screen
    const quickScreen = document.getElementById('screen-sso-quick');
    if (quickScreen) {
        quickScreen.innerHTML = `
            <div class="screen-container">
                <div class="quick-auth-card">
                    <i class="fas fa-check-circle" style="font-size: 5rem; color: var(--color-success);"></i>
                    <h3>تمت المصادقة بنجاح</h3>
                    <p>${currentUser.name}</p>
                </div>
            </div>
        `;
    }
}

function verifyDevice() {
    const items = ['verify-1', 'verify-2', 'verify-3'];
    items.forEach((id, index) => {
        setTimeout(() => {
            document.getElementById(id)?.classList.add('active');
        }, index * 500);
    });
}

function showDashboard() {
    renderModulesWithRBAC(false);
}

function showLockedModules() {
    renderModulesWithRBAC(true);
}

function renderModulesWithRBAC(highlightLocked) {
    const grid = document.getElementById('modules-grid');
    if (!grid) return;

    grid.innerHTML = '';
    modules.forEach(module => {
        const hasAccess = currentUser.permissions.includes(module.id);
        const card = document.createElement('div');
        card.className = 'module-card' + (!hasAccess ? ' locked' : '');
        if (highlightLocked && !hasAccess) {
            card.classList.add('highlight-locked');
        }
        card.innerHTML = `
            <div class="module-icon ${module.color}">
                <i class="fas fa-${module.icon}"></i>
            </div>
            <h4>${module.nameAr}</h4>
            <span class="badge">${module.badge}</span>
            ${!hasAccess ? '<div class="lock-overlay"><i class="fas fa-lock"></i></div>' : ''}
        `;
        grid.appendChild(card);
    });
}

function showModuleAccess() {
    const accessScreen = document.getElementById('screen-module-success');
    if (accessScreen) {
        const allowedModule = modules.find(m => currentUser.permissions.includes(m.id));
        accessScreen.innerHTML = `
            <div class="screen-container">
                <div class="module-success-card">
                    <div class="success-icon-large">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h2>تم الوصول بنجاح</h2>
                    <div class="module-details">
                        <div class="module-icon ${allowedModule.color}" style="width: 100px; height: 100px; font-size: 3rem; margin: 2rem auto;">
                            <i class="fas fa-${allowedModule.icon}"></i>
                        </div>
                        <h3>${allowedModule.nameAr}</h3>
                        <p>المستخدم لديه الصلاحيات المطلوبة</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function attemptAccess() {
    const restrictedModule = modules.find(m => !currentUser.permissions.includes(m.id));
    const indicator = document.getElementById('access-attempt-indicator');
    if (indicator) {
        indicator.innerHTML = `
            <div class="attempt-icon">
                <i class="fas fa-hand-pointer"></i>
            </div>
            <div class="attempt-text">
                <h3>محاولة الوصول</h3>
                <p>${restrictedModule.nameAr}</p>
            </div>
        `;
    }
}

function showAccessDenied() {
    const restrictedModule = modules.find(m => !currentUser.permissions.includes(m.id));

    const event = {
        id: securityEvents.length + 1,
        timestamp: new Date().toISOString(),
        type: 'UNAUTHORIZED_ACCESS',
        user: currentUser.name,
        userId: currentUser.nationalId,
        role: currentUser.roleAr,
        module: restrictedModule?.nameAr,
        moduleId: restrictedModule?.id,
        severity: 'HIGH',
        ip: '192.168.1.' + Math.floor(Math.random() * 255)
    };
    securityEvents.push(event);

    const deniedInfo = document.getElementById('denied-info');
    if (deniedInfo) {
        deniedInfo.innerHTML = `
            <div class="violation-detail">
                <span class="label">المستخدم:</span>
                <span class="value">${event.user}</span>
            </div>
            <div class="violation-detail">
                <span class="label">الدور:</span>
                <span class="value">${event.role}</span>
            </div>
            <div class="violation-detail">
                <span class="label">الوحدة المحظورة:</span>
                <span class="value">${event.module}</span>
            </div>
            <div class="violation-detail">
                <span class="label">عنوان IP:</span>
                <span class="value">${event.ip}</span>
            </div>
            <div class="violation-detail">
                <span class="label">الوقت:</span>
                <span class="value">${new Date().toLocaleTimeString('ar-SA')}</span>
            </div>
        `;
    }
}

function triggerSOCAlert() {
    const latestEvent = securityEvents[securityEvents.length - 1];
    const alertContent = document.getElementById('soc-alert-content');
    if (alertContent) {
        alertContent.innerHTML = `
            <div class="alert-detail">
                <i class="fas fa-exclamation-triangle"></i>
                <span>انتهاك أمني - المستوى: عالي</span>
            </div>
            <div class="alert-detail">
                <i class="fas fa-user"></i>
                <span>${latestEvent.user}</span>
            </div>
            <div class="alert-detail">
                <i class="fas fa-shield-alt"></i>
                <span>محاولة وصول غير مصرح</span>
            </div>
            <div class="alert-progress">
                <div class="progress-bar"></div>
            </div>
            <div class="alert-status">
                <i class="fas fa-check-circle"></i>
                <span>تم إرسال التنبيه لفريق الأمن السيبراني</span>
            </div>
        `;
    }
}

function forwardToMDR() {
    const mdrContent = document.getElementById('mdr-content');
    if (mdrContent) {
        mdrContent.innerHTML = `
            <div class="mdr-step">
                <div class="step-icon active">
                    <i class="fas fa-database"></i>
                </div>
                <span>تسجيل الحدث</span>
            </div>
            <div class="mdr-arrow"><i class="fas fa-arrow-down"></i></div>
            <div class="mdr-step">
                <div class="step-icon active">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <span>التحليل الأمني</span>
            </div>
            <div class="mdr-arrow"><i class="fas fa-arrow-down"></i></div>
            <div class="mdr-step">
                <div class="step-icon active">
                    <i class="fas fa-bell"></i>
                </div>
                <span>إرسال إلى SITE.sa</span>
            </div>
        `;
    }
}

function showEventLogged() {
    const loggedScreen = document.getElementById('screen-event-logged');
    if (loggedScreen) {
        loggedScreen.innerHTML = `
            <div class="screen-container">
                <div class="event-logged-card">
                    <div class="logged-icon">
                        <i class="fas fa-check-double"></i>
                    </div>
                    <h2>تم تسجيل الحدث الأمني</h2>
                    <div class="logged-details">
                        <div class="detail-row">
                            <i class="fas fa-database"></i>
                            <span>تم الحفظ في قاعدة البيانات</span>
                        </div>
                        <div class="detail-row">
                            <i class="fas fa-bell"></i>
                            <span>تم إرسال تنبيه لفريق SOC</span>
                        </div>
                        <div class="detail-row">
                            <i class="fas fa-shield-alt"></i>
                            <span>تم الإرسال إلى SITE.sa</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

function showSOCDashboard() {
    document.getElementById('total-events').textContent = securityEvents.length || Math.floor(Math.random() * 20) + 10;
    document.getElementById('high-severity').textContent = Math.floor(Math.random() * 5) + 3;
    document.getElementById('mdr-status').innerHTML = '<i class="fas fa-check-circle"></i> متصل';

    const tbody = document.getElementById('events-tbody');
    if (tbody && securityEvents.length > 0) {
        tbody.innerHTML = '';
        securityEvents.slice(-5).reverse().forEach(event => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${event.id}</td>
                <td>${new Date(event.timestamp).toLocaleTimeString('ar-SA')}</td>
                <td>${event.user}</td>
                <td>${event.role}</td>
                <td>${event.module}</td>
                <td><span class="severity-badge high">عالي</span></td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function showUBADashboard() {
    // UBA will be populated from uba-data.js
    if (window.initializeUBA) {
        window.initializeUBA();
    }
}

// ==========================================
// ONBOARDING & SDK FUNCTIONS
// ==========================================

function showSDKSetup() {
    const sdkScreen = document.getElementById('screen-sdk-setup');
    if (sdkScreen) {
        sdkScreen.innerHTML = `
            <div class="screen-container">
                <div class="sdk-card">
                    <div class="sdk-header">
                        <i class="fas fa-code"></i>
                        <h2>Nafath SDK Integration</h2>
                        <p>إعداد حزمة تطوير البرمجيات</p>
                    </div>
                    <div class="sdk-steps">
                        <div class="sdk-step active">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h4>تثبيت SDK</h4>
                                <code>npm install @nafath/sso-sdk@2.1.0</code>
                            </div>
                        </div>
                        <div class="sdk-step active">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h4>تكوين API Keys</h4>
                                <div class="api-key-display">
                                    <span>Client ID:</span>
                                    <code>mofa_prod_xk2j9s8d...</code>
                                </div>
                            </div>
                        </div>
                        <div class="sdk-step active">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h4>تفعيل SSL Certificate</h4>
                                <span class="status-badge success">✓ مفعّل</span>
                            </div>
                        </div>
                    </div>
                    <div class="sdk-status">
                        <i class="fas fa-check-circle"></i>
                        <span>SDK v2.1.0 - Ready</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showNafathConfig() {
    const configScreen = document.getElementById('screen-nafath-config');
    if (configScreen) {
        configScreen.innerHTML = `
            <div class="screen-container">
                <div class="config-card">
                    <div class="config-header">
                        <div class="nafath-logo-icon">
                            <i class="fas fa-fingerprint"></i>
                        </div>
                        <h2>ربط نظام نفاذ الوطني</h2>
                    </div>
                    <div class="config-details">
                        <div class="config-item">
                            <i class="fas fa-link"></i>
                            <div>
                                <h4>Callback URL</h4>
                                <code>https://mofa.gov.sa/auth/callback</code>
                            </div>
                            <span class="status-badge success">✓</span>
                        </div>
                        <div class="config-item">
                            <i class="fas fa-shield-alt"></i>
                            <div>
                                <h4>Security Level</h4>
                                <span>High - 2FA Required</span>
                            </div>
                            <span class="status-badge success">✓</span>
                        </div>
                        <div class="config-item">
                            <i class="fas fa-users"></i>
                            <div>
                                <h4>User Sync</h4>
                                <span>Auto-sync enabled</span>
                            </div>
                            <span class="status-badge success">✓</span>
                        </div>
                    </div>
                    <div class="connection-test">
                        <i class="fas fa-check-double"></i>
                        <span>اتصال نفاذ نشط ومستقر</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showRBACAdmin() {
    const rbacScreen = document.getElementById('screen-rbac-admin');
    if (rbacScreen) {
        rbacScreen.innerHTML = `
            <div class="screen-container">
                <div class="rbac-admin-card">
                    <div class="admin-header">
                        <i class="fas fa-user-shield"></i>
                        <h2>لوحة إدارة الصلاحيات (RBAC)</h2>
                        <p>Role-Based Access Control Admin Panel</p>
                    </div>
                    <div class="roles-overview">
                        <div class="role-card diplomat">
                            <div class="role-icon"><i class="fas fa-user-tie"></i></div>
                            <h3>دبلوماسي</h3>
                            <div class="role-count">42 مستخدم</div>
                            <div class="role-permissions">6/6 وحدات</div>
                        </div>
                        <div class="role-card admin">
                            <div class="role-icon"><i class="fas fa-user-cog"></i></div>
                            <h3>موظف إداري</h3>
                            <div class="role-count">87 مستخدم</div>
                            <div class="role-permissions">3/6 وحدات</div>
                        </div>
                        <div class="role-card consultant">
                            <div class="role-icon"><i class="fas fa-user"></i></div>
                            <h3>مستشار خارجي</h3>
                            <div class="role-count">27 مستخدم</div>
                            <div class="role-permissions">1/6 وحدات</div>
                        </div>
                    </div>
                    <div class="admin-actions">
                        <button class="admin-btn primary">+ إضافة دور جديد</button>
                        <button class="admin-btn secondary">تعيين الصلاحيات</button>
                    </div>
                </div>
            </div>
        `;
    }
}

function showAssignPermissions() {
    const assignScreen = document.getElementById('screen-assign-permissions');
    if (assignScreen) {
        assignScreen.innerHTML = `
            <div class="screen-container">
                <div class="assign-card">
                    <div class="assign-header">
                        <h2>تعيين الصلاحيات للأدوار</h2>
                        <p>قم بتحديد الوحدات المتاحة لكل دور</p>
                    </div>
                    <div class="permissions-grid">
                        <div class="permission-row header">
                            <div>الوحدة</div>
                            <div>دبلوماسي</div>
                            <div>موظف إداري</div>
                            <div>مستشار</div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-comments"></i> المراسلات الآمنة</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-folder-open"></i> إدارة الوثائق</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" checked disabled /></div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-broadcast-tower"></i> البرقيات الدبلوماسية</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-globe-americas"></i> شبكة السفارات</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-chart-line"></i> التقارير</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                        </div>
                        <div class="permission-row">
                            <div class="module-name"><i class="fas fa-bell"></i> الإشعارات</div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" checked disabled /></div>
                            <div><input type="checkbox" disabled /></div>
                        </div>
                    </div>
                    <div class="save-status">
                        <i class="fas fa-check-circle"></i>
                        <span>تم حفظ الصلاحيات بنجاح</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showTestAuth() {
    const testScreen = document.getElementById('screen-test-auth');
    if (testScreen) {
        testScreen.innerHTML = `
            <div class="screen-container">
                <div class="test-card">
                    <div class="test-header">
                        <i class="fas fa-vial"></i>
                        <h2>اختبار المصادقة</h2>
                    </div>
                    <div class="test-results">
                        <div class="test-item success">
                            <i class="fas fa-check-circle"></i>
                            <span>SDK Connection</span>
                        </div>
                        <div class="test-item success">
                            <i class="fas fa-check-circle"></i>
                            <span>Nafath Integration</span>
                        </div>
                        <div class="test-item success">
                            <i class="fas fa-check-circle"></i>
                            <span>RBAC Rules</span>
                        </div>
                        <div class="test-item success">
                            <i class="fas fa-check-circle"></i>
                            <span>Session Management</span>
                        </div>
                        <div class="test-item success">
                            <i class="fas fa-check-circle"></i>
                            <span>Token Validation</span>
                        </div>
                    </div>
                    <div class="test-summary">
                        <div class="summary-icon"><i class="fas fa-trophy"></i></div>
                        <h3>جميع الاختبارات نجحت!</h3>
                        <p>النظام جاهز للإنتاج</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function showDeploymentReady() {
    const deployScreen = document.getElementById('screen-deployment-ready');
    if (deployScreen) {
        deployScreen.innerHTML = `
            <div class="screen-container">
                <div class="deploy-card">
                    <div class="deploy-icon">
                        <i class="fas fa-rocket"></i>
                    </div>
                    <h2>جاهز للإنتاج</h2>
                    <p>تم إعداد النظام بنجاح</p>
                    <div class="deploy-checklist">
                        <div class="check-item"><i class="fas fa-check"></i> SDK Integration Complete</div>
                        <div class="check-item"><i class="fas fa-check"></i> Nafath SSO Connected</div>
                        <div class="check-item"><i class="fas fa-check"></i> RBAC Configured</div>
                        <div class="check-item"><i class="fas fa-check"></i> Permissions Assigned</div>
                        <div class="check-item"><i class="fas fa-check"></i> Tests Passed</div>
                    </div>
                    <div class="deploy-stats">
                        <div><strong>156</strong> مستخدمين نشطين</div>
                        <div><strong>3</strong> أدوار محددة</div>
                        <div><strong>6</strong> وحدات منشطة</div>
                    </div>
                </div>
            </div>
        `;
    }
}

function showUserPermissions() {
    const permScreen = document.getElementById('screen-user-permissions');
    if (permScreen) {
        permScreen.innerHTML = `
            <div class="screen-container">
                <div class="user-permissions-card">
                    <div class="permissions-header">
                        <i class="fas fa-user-check"></i>
                        <h2>الصلاحيات المخولة</h2>
                        <p>الخدمات المتاحة حسب دورك</p>
                    </div>
                    <div class="user-info-banner">
                        <div class="user-avatar-large">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <div>
                            <h3>${currentUser.name}</h3>
                            <span class="role-badge role-${currentUser.badge}">${currentUser.roleAr}</span>
                        </div>
                    </div>
                    <div class="services-list">
                        <h3>الخدمات المعينة من قبل المسؤول:</h3>
                        ${modules.map(module => {
            const hasAccess = currentUser.permissions.includes(module.id);
            return `
                                <div class="service-item ${hasAccess ? 'granted' : 'denied'}">
                                    <div class="service-icon ${module.color}">
                                        <i class="fas fa-${module.icon}"></i>
                                    </div>
                                    <div class="service-details">
                                        <h4>${module.nameAr}</h4>
                                        <span>${hasAccess ? 'وصول كامل' : 'غير مصرح'}</span>
                                    </div>
                                    <div class="service-status">
                                        <i class="fas fa-${hasAccess ? 'check-circle' : 'times-circle'}"></i>
                                    </div>
                                </div>
                            `;
        }).join('')}
                    </div>
                    <div class="assigned-by">
                        <i class="fas fa-user-shield"></i>
                        <span>تم التعيين من قبل: مسؤول النظام</span>
                    </div>
                </div>
            </div>
        `;
    }
}

// ==========================================
// AD COMPROMISE PROTECTION SCENARIO
// ==========================================

function showADBreach() {
    const breachScreen = document.getElementById('screen-ad-breach');
    if (breachScreen) {
        breachScreen.innerHTML = `
            <div class="screen-container">
                <div class="breach-card">
                    <div class="breach-header">
                        <div class="breach-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h2>تم اختراق Active Directory</h2>
                        <p>سيناريو الاختراق - Windows AD</p>
                    </div>
                    <div class="breach-details">
                        <div class="breach-item">
                            <i class="fas fa-server"></i>
                            <div>
                                <h4>تم اختراق خادم AD</h4>
                                <p>المهاجم حصل على بيانات اعتماد مسؤول النظام</p>
                            </div>
                        </div>
                        <div class="breach-item">
                            <i class="fas fa-database"></i>
                            <div>
                                <h4>الوصول إلى قاعدة بيانات المستخدمين</h4>
                                <p>156 حساب مستخدم - كلمات المرور المشفرة</p>
                            </div>
                        </div>
                        <div class="breach-item">
                            <i class="fas fa-key"></i>
                            <div>
                                <h4>بيانات الاعتماد المسروقة</h4>
                                <p>Username: ahmad.diplomat@mofa.gov.sa<br/>Password: ••••••••</p>
                            </div>
                        </div>
                    </div>
                    <div class="attacker-badge">
                        <i class="fas fa-user-secret"></i>
                        <span>المهاجم يحاول الآن الوصول لنظام وزارة الخارجية</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showAttackerAttempt() {
    const attemptScreen = document.getElementById('screen-attacker-attempt');
    if (attemptScreen) {
        attemptScreen.innerHTML = `
            <div class="screen-container">
                <div class="attacker-card">
                    <div class="attacker-header">
                        <div class="hacker-icon">
                            <i class="fas fa-user-secret"></i>
                        </div>
                        <h2>محاولة دخول المهاجم</h2>
                    </div>
                    <div class="attempt-steps">
                        <div class="attempt-step completed">
                            <i class="fas fa-check-circle"></i>
                            <span>استخدام بيانات AD المسروقة</span>
                        </div>
                        <div class="attempt-step completed">
                            <i class="fas fa-check-circle"></i>
                            <span>تسجيل الدخول لنظام Windows</span>
                        </div>
                        <div class="attempt-step completed">
                            <i class="fas fa-check-circle"></i>
                            <span>فتح متصفح الإنترنت</span>
                        </div>
                        <div class="attempt-step current">
                            <i class="fas fa-spinner fa-spin"></i>
                            <span>محاولة الوصول لنظام وزارة الخارجية...</span>
                        </div>
                    </div>
                    <div class="stolen-creds">
                        <h4>البيانات المستخدمة:</h4>
                        <code>ahmad.diplomat@mofa.gov.sa / P@ssw0rd123</code>
                    </div>
                </div>
            </div>
        `;
    }
}

function showSSORequired() {
    const ssoScreen = document.getElementById('screen-sso-required');
    if (ssoScreen) {
        ssoScreen.innerHTML = `
            <div class="screen-container">
                <div class="sso-wall-card">
                    <div class="wall-header">
                        <div class="wall-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <h2>نفاذ الوطني مطلوب</h2>
                        <p>SSO External Authentication Required</p>
                    </div>
                    <div class="protection-explanation">
                        <div class="protection-point">
                            <i class="fas fa-times-circle"></i>
                            <div>
                                <h4>بيانات AD غير كافية</h4>
                                <p>النظام لا يقبل بيانات Active Directory مباشرة</p>
                            </div>
                        </div>
                        <div class="protection-point">
                            <i class="fas fa-mobile-alt"></i>
                            <div>
                                <h4>رقم الهوية + OTP مطلوب</h4>
                                <p>يجب المصادقة عبر نفاذ الوطني (الهوية الوطنية + هاتف مسجل)</p>
                            </div>
                        </div>
                        <div class="protection-point">
                            <i class="fas fa-fingerprint"></i>
                            <div>
                                <h4>مصادقة خارجية فقط</h4>
                                <p>Nafath هو المصدر الوحيد للمصادقة - ليس AD</p>
                            </div>
                        </div>
                    </div>
                    <div class="redirect-notice">
                        <i class="fas fa-arrow-right"></i>
                        <span>يتم التحويل تلقائياً إلى نفاذ الوطني...</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showNoOTP() {
    const otpScreen = document.getElementById('screen-no-otp');
    if (otpScreen) {
        otpScreen.innerHTML = `
            <div class="screen-container">
                <div class="no-otp-card">
                    <div class="failed-icon">
                        <i class="fas fa-ban"></i>
                    </div>
                    <h2>المهاجم لا يملك OTP</h2>
                    <div class="missing-factors">
                        <div class="factor-item missing">
                            <i class="fas fa-id-card"></i>
                            <div>
                                <h4>رقم الهوية الوطنية</h4>
                                <p>المهاجم لا يعرف رقم الهوية الحقيقي</p>
                            </div>
                        </div>
                        <div class="factor-item missing">
                            <i class="fas fa-mobile-alt"></i>
                            <div>
                                <h4>الهاتف المسجل</h4>
                                <p>رمز OTP يُرسل لهاتف الموظف الحقيقي فقط</p>
                            </div>
                        </div>
                        <div class="factor-item missing">
                            <i class="fas fa-fingerprint"></i>
                            <div>
                                <h4>بيانات بيومترية</h4>
                                <p>التحقق البيومتري متاح فقط للموظف الحقيقي</p>
                            </div>
                        </div>
                    </div>
                    <div class="security-layer">
                        <i class="fas fa-lock"></i>
                        <span>طبقة الأمان الخارجية تمنع الوصول</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function showAccessBlocked() {
    const blockedScreen = document.getElementById('screen-access-blocked');
    if (blockedScreen) {
        blockedScreen.innerHTML = `
            <div class="screen-container">
                <div class="blocked-card">
                    <div class="blocked-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h2>تم حظر الوصول</h2>
                    <p class="blocked-message">فشلت محاولة المهاجم - نظام نفاذ منع الدخول</p>
                    <div class="failure-reasons">
                        <div class="reason-item">
                            <i class="fas fa-times"></i>
                            <span>لا يوجد رمز OTP صالح</span>
                        </div>
                        <div class="reason-item">
                            <i class="fas fa-times"></i>
                            <span>رقم الهوية غير مطابق</span>
                        </div>
                        <div class="reason-item">
                            <i class="fas fa-times"></i>
                            <span>الهاتف غير مسجل</span>
                        </div>
                    </div>
                    <div class="alert-sent">
                        <i class="fas fa-bell"></i>
                        <div>
                            <h4>تنبيه أمني</h4>
                            <p>تم إرسال تنبيه لفريق الأمن السيبراني ومسؤول AD</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

function showDataSafe() {
    const safeScreen = document.getElementById('screen-data-safe');
    if (safeScreen) {
        safeScreen.innerHTML = `
            <div class="screen-container">
                <div class="safe-card">
                    <div class="safe-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h2>البيانات محمية بالكامل</h2>
                    <p class="safe-message">حتى مع اختراق Active Directory، بيانات وزارة الخارجية آمنة</p>
                    <div class="protection-summary">
                        <div class="summary-item success">
                            <i class="fas fa-database"></i>
                            <div>
                                <h4>بيانات الوزارة</h4>
                                <p>صفر وصول غير مصرح - البيانات سليمة</p>
                            </div>
                        </div>
                        <div class="summary-item success">
                            <i class="fas fa-users"></i>
                            <div>
                                <h4>حسابات المستخدمين</h4>
                                <p>156 حساب محمي بنفاذ الوطني</p>
                            </div>
                        </div>
                        <div class="summary-item success">
                            <i class="fas fa-file-alt"></i>
                            <div>
                                <h4>المستندات السرية</h4>
                                <p>لم يتم الوصول إلى أي ملف</p>
                            </div>
                        </div>
                    </div>
                    <div class="advantage-box">
                        <div class="advantage-icon">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div>
                            <h3>ميزة SSO الخارجي</h3>
                            <p><strong>نفاذ الوطني</strong> يعمل كطبقة حماية مستقلة عن البنية التحتية الداخلية</p>
                            <ul>
                                <li>لا يعتمد على Active Directory</li>
                                <li>مصادقة ثنائية إلزامية (National ID + OTP)</li>
                                <li>حماية من هجمات سرقة بيانات الاعتماد</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// ==========================================
// INITIALIZATION
// ==========================================

window.addEventListener('DOMContentLoaded', () => {
    showScenarioMenu();

    // Attach event listeners
    document.getElementById('btn-prev')?.addEventListener('click', previousStep);
    document.getElementById('btn-next')?.addEventListener('click', nextStep);
    document.getElementById('btn-menu')?.addEventListener('click', showScenarioMenu);
    document.getElementById('btn-autoplay')?.addEventListener('click', toggleAutoPlay);

    // Scenario cards
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.addEventListener('click', () => {
            const scenarioId = card.dataset.scenario;
            if (scenarioId) {
                startScenario(scenarioId);
            }
        });
    });
});
