# MOFA Nafath SSO Demo - Hackathon Project

Advanced SSO demonstration for Ministry of Foreign Affairs with Nafath National Platform integration.

## 🎯 Features

### 6 Interactive Scenarios
1. **SDK Integration & Onboarding** - Complete setup workflow
2. **Normal Authentication Flow** - Full diplomat access with permissions panel
3. **Unauthorized Access** - RBAC violation detection → SOC → MDR
4. **SOC Dashboard** - Security Operations Center monitoring
5. **UBA Dashboard** - User Behavior Analytics with anomaly detection
6. **AD Compromise Protection** - Data remains safe even if Active Directory is breached

### Advanced Security Features
- ✅ **RBAC** - Role-Based Access Control (3 roles: Diplomat, Admin, Consultant)
- ✅ **SOC Integration** - Security Operations Center with real-time alerts
- ✅ **MDR Integration** - SITE.sa Managed Detection & Response
- ✅ **UBA** - User Behavior Analytics with ML-based anomaly detection
- ✅ **Zero Trust** - External SSO independent of internal infrastructure
- ✅ **Permissions Panel** - Visual display of services assigned by admin

### Technical Stack
- Pure Vanilla JavaScript (no frameworks)
- Responsive CSS with Arabic RTL support
- Font Awesome 6.4.0 icons
- Professional MOFA branding

## 🚀 Quick Start

1. Clone this repository
2. Open `index.html` in your browser
3. Select any scenario from the menu
4. Use Next/Previous buttons to control the demo pace

## 📱 Demo Controls

- **Next Button** - Advance to next step
- **Previous Button** - Go back one step
- **Menu Button** - Return to scenario selection
- **Auto-play Toggle** - Enable/disable automatic progression

## 🏆 Hackathon Highlights

**Key Innovation:**
Even if an attacker compromises your Windows Active Directory and steals valid credentials, they **cannot access MOFA data** because:
- Authentication is handled by **Nafath** (external to AD)
- Requires **National ID + OTP** (not AD credentials)
- Provides independent security layer

This demonstrates true **Zero Trust Architecture** and **layered security**.

## 📄 License

Created for Hackathon demonstration purposes.
