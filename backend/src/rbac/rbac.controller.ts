import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { RbacService } from './rbac.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RbacGuard, RequirePermissions } from './guards/rbac.guard';

@Controller('rbac')
@UseGuards(JwtAuthGuard)
export class RbacController {
    constructor(private readonly rbacService: RbacService) { }

    /**
     * GET /api/v1/rbac/roles
     * Get all available roles
     */
    @Get('roles')
    getAllRoles() {
        return {
            success: true,
            roles: this.rbacService.getAllRoles(),
        };
    }

    /**
     * GET /api/v1/rbac/roles/:roleId
     * Get specific role with permissions
     */
    @Get('roles/:roleId')
    getRole(@Param('roleId') roleId: string) {
        const role = this.rbacService.getRoleById(roleId);
        if (!role) {
            return { success: false, error: 'Role not found' };
        }
        return { success: true, role };
    }

    /**
     * GET /api/v1/rbac/permissions
     * Get all available permissions
     */
    @Get('permissions')
    getAllPermissions() {
        return {
            success: true,
            permissions: this.rbacService.getAllPermissions(),
        };
    }

    /**
     * GET /api/v1/rbac/matrix
     * Get full permissions matrix for admin panel
     */
    @Get('matrix')
    @UseGuards(RbacGuard)
    @RequirePermissions('users.view')
    getPermissionsMatrix() {
        return {
            success: true,
            ...this.rbacService.getPermissionsMatrix(),
        };
    }

    /**
     * POST /api/v1/rbac/assign
     * Assign role to user
     */
    @Post('assign')
    @UseGuards(RbacGuard)
    @RequirePermissions('users.view') // In production: 'users.manage'
    async assignRole(
        @Body('nationalId') nationalId: string,
        @Body('roleId') roleId: string,
        @Body('assignedBy') assignedBy: string,
    ) {
        const assignment = await this.rbacService.assignRole(nationalId, roleId, assignedBy);
        return {
            success: true,
            message: 'تم تعيين الصلاحية بنجاح',
            assignment,
        };
    }
}
