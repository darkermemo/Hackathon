/**
 * Nafath SDK TypeScript Interfaces
 */

// Authentication Request
export interface NafathAuthRequest {
    nationalId: string;
    requestId: string;
    serviceCode: string;
    callbackUrl: string;
    timestamp: string;
}

// Authentication Response
export interface NafathAuthResponse {
    success: boolean;
    requestId: string;
    transactionId: string;
    expiresAt: string;
    randomNumber?: number; // Number user confirms in Nafath app
    error?: string;
}

// OTP Verification Request
export interface NafathVerifyRequest {
    transactionId: string;
    otp: string;
    timestamp: string;
}

// OTP Verification Response
export interface NafathVerifyResponse {
    success: boolean;
    verified: boolean;
    accessToken?: string;
    refreshToken?: string;
    userInfo?: NafathUserInfo;
    expiresIn?: number;
    error?: string;
}

// User Information from Nafath
export interface NafathUserInfo {
    nationalId: string;
    nameAr: string;
    nameEn: string;
    dateOfBirth: string;
    gender: 'M' | 'F';
    nationality: string;
    idExpiryDate: string;
    isVerified: boolean;
}

// Session Status
export interface NafathSessionStatus {
    transactionId: string;
    status: 'PENDING' | 'COMPLETED' | 'EXPIRED' | 'CANCELLED' | 'ERROR';
    completedAt?: string;
    userConfirmed: boolean;
}

// SDK Configuration
export interface NafathSdkConfig {
    apiKey: string;
    apiSecret: string;
    baseUrl: string;
    callbackUrl: string;
    timeout: number;
    retryAttempts: number;
}

// Audit Event
export interface NafathAuditEvent {
    eventId: string;
    eventType: 'AUTH_INITIATED' | 'OTP_VERIFIED' | 'AUTH_FAILED' | 'LOGOUT';
    nationalId: string;
    transactionId: string;
    timestamp: string;
    ipAddress: string;
    userAgent: string;
    success: boolean;
    errorMessage?: string;
}
