import { Module } from '@nestjs/common';
import { SocService } from './soc.service';
import { SocController } from './soc.controller';

@Module({
    controllers: [SocController],
    providers: [SocService],
    exports: [SocService],
})
export class SocModule { }
