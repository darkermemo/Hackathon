import { Module } from '@nestjs/common';
import { NafathSdkService } from './nafath-sdk.service';
import { NafathSdkController } from './nafath-sdk.controller';

@Module({
    controllers: [NafathSdkController],
    providers: [NafathSdkService],
    exports: [NafathSdkService],
})
export class NafathSdkModule { }
