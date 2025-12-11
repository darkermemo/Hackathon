import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { SocService, EventStatus } from './soc.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RbacGuard, RequirePermissions } from '../rbac/guards/rbac.guard';

@Controller('soc')
@UseGuards(JwtAuthGuard)
export class SocController {
    constructor(private readonly socService: SocService) { }

    /**
     * GET /api/v1/soc/dashboard
     * Get SOC dashboard metrics
     */
    @Get('dashboard')
    @UseGuards(RbacGuard)
    @RequirePermissions('reports.view')
    getDashboard() {
        return {
            success: true,
            ...this.socService.getDashboardMetrics(),
        };
    }

    /**
     * GET /api/v1/soc/events
     * Get all security events
     */
    @Get('events')
    @UseGuards(RbacGuard)
    @RequirePermissions('reports.view')
    getAllEvents() {
        return {
            success: true,
            events: this.socService.getDashboardMetrics().recentEvents,
        };
    }

    /**
     * GET /api/v1/soc/events/type/:type
     * Get events by type
     */
    @Get('events/type/:type')
    @UseGuards(RbacGuard)
    @RequirePermissions('reports.view')
    getEventsByType(@Param('type') type: string) {
        return {
            success: true,
            events: this.socService.getEventsByType(type),
        };
    }

    /**
     * GET /api/v1/soc/events/user/:nationalId
     * Get events for specific user
     */
    @Get('events/user/:nationalId')
    @UseGuards(RbacGuard)
    @RequirePermissions('reports.view')
    getEventsByUser(@Param('nationalId') nationalId: string) {
        return {
            success: true,
            events: this.socService.getEventsByUser(nationalId),
        };
    }

    /**
     * POST /api/v1/soc/events/:eventId/status
     * Update event status
     */
    @Post('events/:eventId/status')
    @UseGuards(RbacGuard)
    @RequirePermissions('reports.view')
    updateEventStatus(
        @Param('eventId') eventId: string,
        @Body('status') status: EventStatus,
    ) {
        const event = this.socService.updateEventStatus(eventId, status);
        if (!event) {
            return { success: false, error: 'Event not found' };
        }
        return {
            success: true,
            message: 'تم تحديث حالة الحدث',
            event,
        };
    }
}
