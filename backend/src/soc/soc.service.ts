/**
 * SOC - Security Operations Center Service
 * 
 * Handles security event logging, alerting, and MDR integration
 * Integrates with SITE.sa for Managed Detection & Response
 */

import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

export type EventSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type EventStatus = 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';

export interface SecurityEvent {
    id: string;
    type: string;
    severity: EventSeverity;
    status: EventStatus;
    timestamp: string;
    source: string;
    nationalId?: string;
    ipAddress: string;
    userAgent: string;
    details: Record<string, any>;
    mdrReported: boolean;
}

export interface SocDashboardMetrics {
    totalEvents: number;
    criticalAlerts: number;
    activeIncidents: number;
    resolvedToday: number;
    eventsBySeverity: Record<EventSeverity, number>;
    recentEvents: SecurityEvent[];
}

@Injectable()
export class SocService {
    private events: SecurityEvent[] = [];
    private readonly mdrEndpoint: string;
    private readonly mdrApiKey: string;

    constructor(private configService: ConfigService) {
        this.mdrEndpoint = this.configService.get<string>('SITE_MDR_ENDPOINT', 'https://mdr.site.sa/api/v1/events');
        this.mdrApiKey = this.configService.get<string>('SITE_MDR_API_KEY');
    }

    /**
     * Log a security event
     */
    async logEvent(event: Omit<SecurityEvent, 'id' | 'status' | 'mdrReported'>): Promise<SecurityEvent> {
        const newEvent: SecurityEvent = {
            ...event,
            id: this.generateEventId(),
            status: 'NEW',
            mdrReported: false,
        };

        this.events.push(newEvent);

        // Auto-escalate critical events to MDR
        if (event.severity === 'HIGH' || event.severity === 'CRITICAL') {
            await this.reportToMdr(newEvent);
            newEvent.mdrReported = true;
        }

        // Log to console for debugging
        console.log('SOC_EVENT:', JSON.stringify(newEvent, null, 2));

        return newEvent;
    }

    /**
     * Log authentication failure
     */
    async logAuthFailure(nationalId: string, ipAddress: string, userAgent: string, reason: string): Promise<SecurityEvent> {
        return this.logEvent({
            type: 'AUTH_FAILURE',
            severity: 'MEDIUM',
            timestamp: new Date().toISOString(),
            source: 'NAFATH_SSO',
            nationalId,
            ipAddress,
            userAgent,
            details: { reason },
        });
    }

    /**
     * Log RBAC violation
     */
    async logRbacViolation(
        nationalId: string,
        role: string,
        attemptedResource: string,
        ipAddress: string,
        userAgent: string,
    ): Promise<SecurityEvent> {
        return this.logEvent({
            type: 'RBAC_VIOLATION',
            severity: 'HIGH',
            timestamp: new Date().toISOString(),
            source: 'RBAC_GUARD',
            nationalId,
            ipAddress,
            userAgent,
            details: {
                role,
                attemptedResource,
                message: 'محاولة وصول غير مصرح بها',
            },
        });
    }

    /**
     * Log suspicious activity (UBA detection)
     */
    async logSuspiciousActivity(
        nationalId: string,
        activityType: string,
        riskScore: number,
        ipAddress: string,
        details: Record<string, any>,
    ): Promise<SecurityEvent> {
        const severity: EventSeverity = riskScore >= 80 ? 'CRITICAL' : riskScore >= 60 ? 'HIGH' : 'MEDIUM';

        return this.logEvent({
            type: 'SUSPICIOUS_ACTIVITY',
            severity,
            timestamp: new Date().toISOString(),
            source: 'UBA_ENGINE',
            nationalId,
            ipAddress,
            userAgent: '',
            details: {
                activityType,
                riskScore,
                ...details,
            },
        });
    }

    /**
     * Log session hijacking attempt
     */
    async logSessionHijack(
        nationalId: string,
        originalIp: string,
        newIp: string,
        userAgent: string,
    ): Promise<SecurityEvent> {
        return this.logEvent({
            type: 'SESSION_HIJACK_ATTEMPT',
            severity: 'CRITICAL',
            timestamp: new Date().toISOString(),
            source: 'SESSION_MONITOR',
            nationalId,
            ipAddress: newIp,
            userAgent,
            details: {
                originalIp,
                newIp,
                message: 'محاولة اختطاف جلسة - تم رصد IP مختلف',
            },
        });
    }

    /**
     * Report event to SITE.sa MDR
     */
    async reportToMdr(event: SecurityEvent): Promise<boolean> {
        try {
            await axios.post(this.mdrEndpoint, {
                source: 'MOFA_SSO',
                event: {
                    id: event.id,
                    type: event.type,
                    severity: event.severity,
                    timestamp: event.timestamp,
                    details: event.details,
                },
                organization: 'MOFA',
                priority: event.severity === 'CRITICAL' ? 1 : 2,
            }, {
                headers: {
                    'Authorization': `Bearer ${this.mdrApiKey}`,
                    'Content-Type': 'application/json',
                },
            });

            console.log('MDR_REPORTED:', event.id);
            return true;
        } catch (error) {
            console.error('MDR_REPORT_FAILED:', error.message);
            return false;
        }
    }

    /**
     * Get SOC dashboard metrics
     */
    getDashboardMetrics(): SocDashboardMetrics {
        const today = new Date().toISOString().split('T')[0];

        const eventsBySeverity: Record<EventSeverity, number> = {
            LOW: 0,
            MEDIUM: 0,
            HIGH: 0,
            CRITICAL: 0,
        };

        let resolvedToday = 0;
        let criticalAlerts = 0;
        let activeIncidents = 0;

        this.events.forEach(event => {
            eventsBySeverity[event.severity]++;

            if (event.severity === 'CRITICAL') criticalAlerts++;
            if (event.status !== 'RESOLVED' && event.status !== 'FALSE_POSITIVE') activeIncidents++;
            if (event.status === 'RESOLVED' && event.timestamp.startsWith(today)) resolvedToday++;
        });

        return {
            totalEvents: this.events.length,
            criticalAlerts,
            activeIncidents,
            resolvedToday,
            eventsBySeverity,
            recentEvents: this.events.slice(-10).reverse(),
        };
    }

    /**
     * Get events by type
     */
    getEventsByType(type: string): SecurityEvent[] {
        return this.events.filter(e => e.type === type);
    }

    /**
     * Get events by national ID
     */
    getEventsByUser(nationalId: string): SecurityEvent[] {
        return this.events.filter(e => e.nationalId === nationalId);
    }

    /**
     * Update event status
     */
    updateEventStatus(eventId: string, status: EventStatus): SecurityEvent | null {
        const event = this.events.find(e => e.id === eventId);
        if (event) {
            event.status = status;
            return event;
        }
        return null;
    }

    /**
     * Generate unique event ID
     */
    private generateEventId(): string {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2, 8);
        return `SOC-${timestamp}-${random}`.toUpperCase();
    }
}
