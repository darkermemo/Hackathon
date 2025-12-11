import { Controller, Post, Get, Body, Param, HttpCode, HttpStatus } from '@nestjs/common';
import { NafathSdkService } from './nafath-sdk.service';
import { InitiateAuthDto, VerifyOtpDto } from './dto/nafath.dto';

@Controller('nafath')
export class NafathSdkController {
    constructor(private readonly nafathService: NafathSdkService) { }

    /**
     * POST /api/v1/nafath/auth/initiate
     * Start Nafath authentication process
     */
    @Post('auth/initiate')
    @HttpCode(HttpStatus.OK)
    async initiateAuth(@Body() dto: InitiateAuthDto) {
        return this.nafathService.initiateAuth(dto.nationalId);
    }

    /**
     * POST /api/v1/nafath/auth/verify
     * Verify OTP from Nafath
     */
    @Post('auth/verify')
    @HttpCode(HttpStatus.OK)
    async verifyOtp(@Body() dto: VerifyOtpDto) {
        return this.nafathService.verifyOtp(dto.transactionId, dto.otp);
    }

    /**
     * GET /api/v1/nafath/session/:transactionId/status
     * Check authentication session status
     */
    @Get('session/:transactionId/status')
    async getSessionStatus(@Param('transactionId') transactionId: string) {
        return this.nafathService.checkSessionStatus(transactionId);
    }

    /**
     * POST /api/v1/nafath/auth/refresh
     * Refresh access token
     */
    @Post('auth/refresh')
    @HttpCode(HttpStatus.OK)
    async refreshToken(@Body('refreshToken') refreshToken: string) {
        return this.nafathService.refreshToken(refreshToken);
    }

    /**
     * POST /api/v1/nafath/auth/logout
     * Logout and invalidate session
     */
    @Post('auth/logout')
    @HttpCode(HttpStatus.OK)
    async logout(@Body('accessToken') accessToken: string) {
        const success = await this.nafathService.logout(accessToken);
        return { success, message: success ? 'Logged out successfully' : 'Logout failed' };
    }
}
