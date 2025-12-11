/**
 * RBAC - Role-Based Access Control Service
 * 
 * Manages roles, permissions, and access control for MOFA SSO
 */

import { Injectable, ForbiddenException } from '@nestjs/common';

export interface Role {
    id: string;
    name: string;
    nameAr: string;
    description: string;
    permissions: string[];
    level: number; // Hierarchy level for inheritance
}

export interface Permission {
    id: string;
    name: string;
    nameAr: string;
    module: string;
    action: 'view' | 'create' | 'update' | 'delete' | 'manage';
}

export interface UserRole {
    nationalId: string;
    roleId: string;
    assignedBy: string;
    assignedAt: Date;
    expiresAt?: Date;
}

@Injectable()
export class RbacService {
    // Predefined roles for MOFA
    private readonly roles: Role[] = [
        {
            id: 'diplomat',
            name: 'Diplomat',
            nameAr: 'دبلوماسي',
            description: 'Full access to diplomatic services and consular affairs',
            level: 3,
            permissions: [
                'passport.view', 'passport.renew', 'passport.apply',
                'consular.access', 'consular.submit',
                'travel.manage', 'travel.request',
                'documents.view', 'documents.upload', 'documents.download',
                'embassy.communicate',
                'visa.view', 'visa.process',
            ],
        },
        {
            id: 'admin_staff',
            name: 'Admin Staff',
            nameAr: 'موظف إداري',
            description: 'Administrative access to internal systems',
            level: 2,
            permissions: [
                'documents.view', 'documents.upload',
                'travel.view',
                'reports.view', 'reports.generate',
                'users.view',
            ],
        },
        {
            id: 'consultant',
            name: 'Consultant',
            nameAr: 'مستشار',
            description: 'Limited view-only access',
            level: 1,
            permissions: [
                'documents.view',
                'reports.view',
            ],
        },
    ];

    // Predefined permissions
    private readonly permissions: Permission[] = [
        { id: 'passport.view', name: 'View Passport', nameAr: 'عرض الجواز', module: 'passport', action: 'view' },
        { id: 'passport.renew', name: 'Renew Passport', nameAr: 'تجديد الجواز', module: 'passport', action: 'update' },
        { id: 'passport.apply', name: 'Apply Passport', nameAr: 'طلب جواز جديد', module: 'passport', action: 'create' },
        { id: 'consular.access', name: 'Consular Access', nameAr: 'الخدمات القنصلية', module: 'consular', action: 'view' },
        { id: 'consular.submit', name: 'Submit Consular Request', nameAr: 'تقديم طلب قنصلي', module: 'consular', action: 'create' },
        { id: 'travel.manage', name: 'Manage Travel', nameAr: 'إدارة السفر', module: 'travel', action: 'manage' },
        { id: 'travel.view', name: 'View Travel', nameAr: 'عرض السفر', module: 'travel', action: 'view' },
        { id: 'travel.request', name: 'Request Travel', nameAr: 'طلب سفر', module: 'travel', action: 'create' },
        { id: 'documents.view', name: 'View Documents', nameAr: 'عرض المستندات', module: 'documents', action: 'view' },
        { id: 'documents.upload', name: 'Upload Documents', nameAr: 'رفع المستندات', module: 'documents', action: 'create' },
        { id: 'documents.download', name: 'Download Documents', nameAr: 'تحميل المستندات', module: 'documents', action: 'view' },
        { id: 'embassy.communicate', name: 'Embassy Communication', nameAr: 'التواصل مع السفارة', module: 'embassy', action: 'manage' },
        { id: 'visa.view', name: 'View Visa', nameAr: 'عرض التأشيرة', module: 'visa', action: 'view' },
        { id: 'visa.process', name: 'Process Visa', nameAr: 'معالجة التأشيرة', module: 'visa', action: 'update' },
        { id: 'reports.view', name: 'View Reports', nameAr: 'عرض التقارير', module: 'reports', action: 'view' },
        { id: 'reports.generate', name: 'Generate Reports', nameAr: 'إنشاء التقارير', module: 'reports', action: 'create' },
        { id: 'users.view', name: 'View Users', nameAr: 'عرض المستخدمين', module: 'users', action: 'view' },
    ];

    /**
     * Get all roles
     */
    getAllRoles(): Role[] {
        return this.roles;
    }

    /**
     * Get role by ID
     */
    getRoleById(roleId: string): Role | undefined {
        return this.roles.find(r => r.id === roleId);
    }

    /**
     * Get all permissions
     */
    getAllPermissions(): Permission[] {
        return this.permissions;
    }

    /**
     * Get permissions for a role
     */
    getRolePermissions(roleId: string): string[] {
        const role = this.getRoleById(roleId);
        return role?.permissions || [];
    }

    /**
     * Check if user has specific permission
     */
    hasPermission(userPermissions: string[], requiredPermission: string): boolean {
        return userPermissions.includes(requiredPermission);
    }

    /**
     * Check if user has any of the required permissions
     */
    hasAnyPermission(userPermissions: string[], requiredPermissions: string[]): boolean {
        return requiredPermissions.some(p => userPermissions.includes(p));
    }

    /**
     * Check if user has all required permissions
     */
    hasAllPermissions(userPermissions: string[], requiredPermissions: string[]): boolean {
        return requiredPermissions.every(p => userPermissions.includes(p));
    }

    /**
     * Validate access and throw if unauthorized
     */
    validateAccess(userPermissions: string[], requiredPermission: string): void {
        if (!this.hasPermission(userPermissions, requiredPermission)) {
            throw new ForbiddenException({
                error: 'ACCESS_DENIED',
                message: 'ليس لديك صلاحية للوصول لهذا المورد',
                requiredPermission,
                timestamp: new Date().toISOString(),
            });
        }
    }

    /**
     * Get permissions matrix for admin panel
     */
    getPermissionsMatrix(): { roles: Role[]; permissions: Permission[]; matrix: Record<string, string[]> } {
        const matrix: Record<string, string[]> = {};

        this.roles.forEach(role => {
            matrix[role.id] = role.permissions;
        });

        return {
            roles: this.roles,
            permissions: this.permissions,
            matrix,
        };
    }

    /**
     * Assign role to user (would persist to database in production)
     */
    async assignRole(nationalId: string, roleId: string, assignedBy: string): Promise<UserRole> {
        const role = this.getRoleById(roleId);
        if (!role) {
            throw new ForbiddenException('Invalid role');
        }

        const assignment: UserRole = {
            nationalId,
            roleId,
            assignedBy,
            assignedAt: new Date(),
        };

        // In production: save to database
        // await this.userRoleRepository.save(assignment);

        return assignment;
    }
}
