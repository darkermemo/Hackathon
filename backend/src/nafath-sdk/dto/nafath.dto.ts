import { IsString, IsNotEmpty, Length, Matches } from 'class-validator';

export class InitiateAuthDto {
    @IsString()
    @IsNotEmpty()
    @Length(10, 10, { message: 'National ID must be exactly 10 digits' })
    @Matches(/^[0-9]+$/, { message: 'National ID must contain only numbers' })
    nationalId: string;
}

export class VerifyOtpDto {
    @IsString()
    @IsNotEmpty()
    transactionId: string;

    @IsString()
    @IsNotEmpty()
    @Length(4, 6, { message: 'OTP must be 4-6 digits' })
    @Matches(/^[0-9]+$/, { message: 'OTP must contain only numbers' })
    otp: string;
}

export class RefreshTokenDto {
    @IsString()
    @IsNotEmpty()
    refreshToken: string;
}
