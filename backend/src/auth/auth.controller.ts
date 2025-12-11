import { Controller, Post, Body, UseGuards, Get, Request, HttpCode, HttpStatus } from '@nestjs/common';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './guards/jwt-auth.guard';

@Controller('auth')
export class AuthController {
    constructor(private readonly authService: AuthService) { }

    /**
     * POST /api/v1/auth/login
     * Login with Nafath credentials
     */
    @Post('login')
    @HttpCode(HttpStatus.OK)
    async login(
        @Body('transactionId') transactionId: string,
        @Body('otp') otp: string,
    ) {
        const result = await this.authService.authenticateWithNafath(transactionId, otp);
        return {
            success: true,
            accessToken: result.accessToken,
            user: {
                nationalId: result.user.nationalId,
                name: result.user.name,
                role: result.user.role,
                permissions: result.user.permissions,
            },
        };
    }

    /**
     * GET /api/v1/auth/me
     * Get current user info
     */
    @UseGuards(JwtAuthGuard)
    @Get('me')
    async getCurrentUser(@Request() req: any) {
        return {
            success: true,
            user: req.user,
        };
    }

    /**
     * POST /api/v1/auth/logout
     * Logout current user
     */
    @UseGuards(JwtAuthGuard)
    @Post('logout')
    @HttpCode(HttpStatus.OK)
    async logout(@Request() req: any) {
        const success = await this.authService.logout(req.user.nafathToken);
        return {
            success,
            message: success ? 'تم تسجيل الخروج بنجاح' : 'فشل تسجيل الخروج',
        };
    }
}
