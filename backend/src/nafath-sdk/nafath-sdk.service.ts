/**
 * MOFA Nafath SDK - National SSO Integration
 * 
 * This SDK provides seamless integration with Saudi Arabia's
 * National Single Sign-On platform (Nafath) for government services.
 * 
 * Features:
 * - National ID Authentication
 * - OTP Verification
 * - Biometric Support
 * - Session Management
 * - Audit Logging
 */

import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import {
    NafathAuthRequest,
    NafathAuthResponse,
    NafathVerifyRequest,
    NafathVerifyResponse,
    NafathUserInfo,
    NafathSessionStatus,
} from './interfaces/nafath.interface';

@Injectable()
export class NafathSdkService {
    private readonly client: AxiosInstance;
    private readonly apiKey: string;
    private readonly apiSecret: string;
    private readonly baseUrl: string;

    constructor(private configService: ConfigService) {
        this.apiKey = this.configService.get<string>('NAFATH_API_KEY');
        this.apiSecret = this.configService.get<string>('NAFATH_API_SECRET');
        this.baseUrl = this.configService.get<string>('NAFATH_BASE_URL', 'https://nafath.api.gov.sa/v2');

        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey,
                'X-Request-ID': uuidv4(),
            },
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => this.handleApiError(error),
        );
    }

    /**
     * Initiate Nafath authentication for a user
     * Sends OTP to the user's registered mobile number
     */
    async initiateAuth(nationalId: string): Promise<NafathAuthResponse> {
        const requestId = uuidv4();

        const request: NafathAuthRequest = {
            nationalId,
            requestId,
            serviceCode: 'MOFA_SSO',
            callbackUrl: this.configService.get<string>('NAFATH_CALLBACK_URL'),
            timestamp: new Date().toISOString(),
        };

        try {
            const response = await this.client.post('/auth/initiate', request, {
                headers: {
                    'X-Signature': this.generateSignature(request),
                },
            });

            return {
                success: true,
                requestId,
                transactionId: response.data.transactionId,
                expiresAt: response.data.expiresAt,
                randomNumber: response.data.randomNumber, // User confirms this number in Nafath app
            };
        } catch (error) {
            throw new HttpException(
                'Failed to initiate Nafath authentication',
                HttpStatus.SERVICE_UNAVAILABLE,
            );
        }
    }

    /**
     * Verify OTP entered by the user
     */
    async verifyOtp(transactionId: string, otp: string): Promise<NafathVerifyResponse> {
        const request: NafathVerifyRequest = {
            transactionId,
            otp,
            timestamp: new Date().toISOString(),
        };

        try {
            const response = await this.client.post('/auth/verify', request, {
                headers: {
                    'X-Signature': this.generateSignature(request),
                },
            });

            if (response.data.verified) {
                return {
                    success: true,
                    verified: true,
                    accessToken: response.data.accessToken,
                    refreshToken: response.data.refreshToken,
                    userInfo: response.data.userInfo,
                    expiresIn: response.data.expiresIn,
                };
            }

            return {
                success: false,
                verified: false,
                error: 'OTP verification failed',
            };
        } catch (error) {
            throw new HttpException(
                'OTP verification failed',
                HttpStatus.UNAUTHORIZED,
            );
        }
    }

    /**
     * Get user information from Nafath token
     */
    async getUserInfo(accessToken: string): Promise<NafathUserInfo> {
        try {
            const response = await this.client.get('/user/info', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });

            return {
                nationalId: response.data.nationalId,
                nameAr: response.data.nameAr,
                nameEn: response.data.nameEn,
                dateOfBirth: response.data.dateOfBirth,
                gender: response.data.gender,
                nationality: response.data.nationality,
                idExpiryDate: response.data.idExpiryDate,
                isVerified: true,
            };
        } catch (error) {
            throw new HttpException(
                'Failed to retrieve user information',
                HttpStatus.UNAUTHORIZED,
            );
        }
    }

    /**
     * Check session status
     */
    async checkSessionStatus(transactionId: string): Promise<NafathSessionStatus> {
        try {
            const response = await this.client.get(`/session/${transactionId}/status`);

            return {
                transactionId,
                status: response.data.status, // 'PENDING' | 'COMPLETED' | 'EXPIRED' | 'CANCELLED'
                completedAt: response.data.completedAt,
                userConfirmed: response.data.userConfirmed,
            };
        } catch (error) {
            return {
                transactionId,
                status: 'ERROR',
                userConfirmed: false,
            };
        }
    }

    /**
     * Refresh access token
     */
    async refreshToken(refreshToken: string): Promise<{ accessToken: string; expiresIn: number }> {
        try {
            const response = await this.client.post('/auth/refresh', {
                refreshToken,
                timestamp: new Date().toISOString(),
            });

            return {
                accessToken: response.data.accessToken,
                expiresIn: response.data.expiresIn,
            };
        } catch (error) {
            throw new HttpException(
                'Token refresh failed',
                HttpStatus.UNAUTHORIZED,
            );
        }
    }

    /**
     * Logout and invalidate session
     */
    async logout(accessToken: string): Promise<boolean> {
        try {
            await this.client.post('/auth/logout', null, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Generate HMAC signature for API requests
     */
    private generateSignature(payload: object): string {
        const crypto = require('crypto');
        const data = JSON.stringify(payload);
        return crypto
            .createHmac('sha256', this.apiSecret)
            .update(data)
            .digest('hex');
    }

    /**
     * Handle API errors with proper logging
     */
    private handleApiError(error: any) {
        console.error('Nafath API Error:', {
            status: error.response?.status,
            message: error.response?.data?.message,
            timestamp: new Date().toISOString(),
        });

        throw new HttpException(
            error.response?.data?.message || 'Nafath service unavailable',
            error.response?.status || HttpStatus.SERVICE_UNAVAILABLE,
        );
    }
}
