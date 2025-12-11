import { Injectable, CanActivate, ExecutionContext, ForbiddenException, SetMetadata } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { RbacService } from '../rbac.service';

export const PERMISSIONS_KEY = 'permissions';
export const RequirePermissions = (...permissions: string[]) => SetMetadata(PERMISSIONS_KEY, permissions);

@Injectable()
export class RbacGuard implements CanActivate {
    constructor(
        private reflector: Reflector,
        private rbacService: RbacService,
    ) { }

    canActivate(context: ExecutionContext): boolean {
        const requiredPermissions = this.reflector.getAllAndOverride<string[]>(PERMISSIONS_KEY, [
            context.getHandler(),
            context.getClass(),
        ]);

        // If no permissions required, allow access
        if (!requiredPermissions || requiredPermissions.length === 0) {
            return true;
        }

        const request = context.switchToHttp().getRequest();
        const user = request.user;

        if (!user || !user.permissions) {
            throw new ForbiddenException({
                error: 'ACCESS_DENIED',
                message: 'يجب تسجيل الدخول للوصول لهذا المورد',
                timestamp: new Date().toISOString(),
            });
        }

        const hasPermission = this.rbacService.hasAnyPermission(user.permissions, requiredPermissions);

        if (!hasPermission) {
            // Log unauthorized access attempt for SOC
            console.warn('RBAC_VIOLATION:', {
                user: user.nationalId,
                role: user.role,
                attempted: requiredPermissions,
                userPermissions: user.permissions,
                timestamp: new Date().toISOString(),
                ip: request.ip,
            });

            throw new ForbiddenException({
                error: 'RBAC_VIOLATION',
                message: 'ليس لديك صلاحية للوصول لهذا المورد',
                requiredPermissions,
                userRole: user.role,
                timestamp: new Date().toISOString(),
            });
        }

        return true;
    }
}
