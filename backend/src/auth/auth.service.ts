import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { NafathSdkService } from '../nafath-sdk/nafath-sdk.service';
import { NafathUserInfo } from '../nafath-sdk/interfaces/nafath.interface';

export interface JwtPayload {
    sub: string; // nationalId
    name: string;
    role: string;
    permissions: string[];
    iat?: number;
    exp?: number;
}

export interface AuthenticatedUser {
    nationalId: string;
    name: string;
    role: string;
    permissions: string[];
    nafathToken: string;
}

@Injectable()
export class AuthService {
    constructor(
        private readonly jwtService: JwtService,
        private readonly nafathService: NafathSdkService,
    ) { }

    /**
     * Authenticate user via Nafath and issue JWT
     */
    async authenticateWithNafath(
        transactionId: string,
        otp: string,
    ): Promise<{ accessToken: string; user: AuthenticatedUser }> {
        // Verify OTP with Nafath
        const nafathResponse = await this.nafathService.verifyOtp(transactionId, otp);

        if (!nafathResponse.verified || !nafathResponse.userInfo) {
            throw new UnauthorizedException('Nafath authentication failed');
        }

        const userInfo = nafathResponse.userInfo;

        // Get user role and permissions from database (mocked here)
        const { role, permissions } = await this.getUserRoleAndPermissions(userInfo.nationalId);

        // Create JWT payload
        const payload: JwtPayload = {
            sub: userInfo.nationalId,
            name: userInfo.nameAr,
            role,
            permissions,
        };

        // Sign JWT
        const accessToken = this.jwtService.sign(payload);

        return {
            accessToken,
            user: {
                nationalId: userInfo.nationalId,
                name: userInfo.nameAr,
                role,
                permissions,
                nafathToken: nafathResponse.accessToken,
            },
        };
    }

    /**
     * Validate JWT and return user
     */
    async validateToken(token: string): Promise<JwtPayload> {
        try {
            return this.jwtService.verify<JwtPayload>(token);
        } catch (error) {
            throw new UnauthorizedException('Invalid or expired token');
        }
    }

    /**
     * Get user role and permissions from database
     * In production, this would query the database
     */
    private async getUserRoleAndPermissions(
        nationalId: string,
    ): Promise<{ role: string; permissions: string[] }> {
        // Mock implementation - would be database lookup in production
        const roleMap: Record<string, { role: string; permissions: string[] }> = {
            // Diplomat role - full access
            default: {
                role: 'DIPLOMAT',
                permissions: [
                    'passport.view',
                    'passport.renew',
                    'consular.access',
                    'travel.manage',
                    'documents.view',
                    'documents.upload',
                    'embassy.communicate',
                    'visa.process',
                ],
            },
        };

        return roleMap[nationalId] || roleMap.default;
    }

    /**
     * Logout user (invalidate session)
     */
    async logout(nafathToken: string): Promise<boolean> {
        return this.nafathService.logout(nafathToken);
    }
}
