import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './auth/auth.module';
import { NafathSdkModule } from './nafath-sdk/nafath-sdk.module';
import { RbacModule } from './rbac/rbac.module';
import { SocModule } from './soc/soc.module';

@Module({
    imports: [
        // Configuration
        ConfigModule.forRoot({
            isGlobal: true,
            envFilePath: ['.env.local', '.env'],
        }),

        // Core Modules
        AuthModule,
        NafathSdkModule,
        RbacModule,
        SocModule,
    ],
})
export class AppModule { }
