# MOFA SSO Backend

NestJS backend with Nafath SDK integration for MOFA Single Sign-On.

## Features

- 🔐 **Nafath SDK** - National SSO integration with OTP verification
- 🛡️ **RBAC** - Role-Based Access Control with 3 predefined roles
- 📊 **SOC Integration** - Security event logging and alerting
- 🚨 **MDR Integration** - SITE.sa Managed Detection & Response

## Project Structure

```
backend/
├── src/
│   ├── auth/               # Authentication module
│   │   ├── guards/         # JWT guards and strategies
│   │   ├── auth.controller.ts
│   │   ├── auth.module.ts
│   │   └── auth.service.ts
│   │
│   ├── nafath-sdk/         # Nafath SDK module
│   │   ├── dto/            # Data Transfer Objects
│   │   ├── interfaces/     # TypeScript interfaces
│   │   ├── nafath-sdk.controller.ts
│   │   ├── nafath-sdk.module.ts
│   │   └── nafath-sdk.service.ts
│   │
│   ├── rbac/               # RBAC module
│   │   ├── guards/         # Permission guards
│   │   ├── rbac.controller.ts
│   │   ├── rbac.module.ts
│   │   └── rbac.service.ts
│   │
│   ├── soc/                # SOC module
│   │   ├── soc.controller.ts
│   │   ├── soc.module.ts
│   │   └── soc.service.ts
│   │
│   ├── app.module.ts
│   └── main.ts
│
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

## API Endpoints

### Nafath SDK
- `POST /api/v1/nafath/auth/initiate` - Start authentication
- `POST /api/v1/nafath/auth/verify` - Verify OTP
- `GET /api/v1/nafath/session/:id/status` - Check session status
- `POST /api/v1/nafath/auth/refresh` - Refresh token
- `POST /api/v1/nafath/auth/logout` - Logout

### Authentication
- `POST /api/v1/auth/login` - Login with Nafath
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### RBAC
- `GET /api/v1/rbac/roles` - Get all roles
- `GET /api/v1/rbac/permissions` - Get all permissions
- `GET /api/v1/rbac/matrix` - Get permission matrix
- `POST /api/v1/rbac/assign` - Assign role to user

### SOC
- `GET /api/v1/soc/dashboard` - Get SOC metrics
- `GET /api/v1/soc/events` - Get security events
- `POST /api/v1/soc/events/:id/status` - Update event status

## Installation

```bash
npm install
```

## Running

```bash
# Development
npm run start:dev

# Production
npm run build
npm run start:prod
```

## Security Features

1. **External SSO** - Authentication separate from AD
2. **JWT Tokens** - Short-lived access tokens
3. **RBAC Guards** - Permission-based access control
4. **Event Logging** - All security events logged
5. **MDR Integration** - Critical events auto-reported
