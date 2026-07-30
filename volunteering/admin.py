from django.contrib import admin
from .models import (
    Event, EventRegistration, ImpactLog, Badge,
    VolunteerBadge, Certificate, CoordinatorMessage,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'is_published', 'seats_taken']
    list_filter = ['is_published', 'date']
    search_fields = ['title', 'location']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'event', 'status', 'hours_logged', 'registered_at']
    list_filter = ['status']
    search_fields = ['volunteer__email', 'event__title']
    actions = ['mark_as_attended']

    def mark_as_attended(self, request, queryset):
        for reg in queryset:
            if reg.status != 'attended':
                from . import services
                services.mark_attendance(reg, reg.hours_logged or 1)
        self.message_user(request, f'{queryset.count()} registration(s) marked as attended.')
    mark_as_attended.short_description = 'Mark selected as attended (with logged hours)'


@admin.register(ImpactLog)
class ImpactLogAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'hours', 'date', 'is_approved', 'approved_by']
    list_filter = ['is_approved']
    search_fields = ['volunteer__email', 'description']
    actions = ['approve_logs']

    def approve_logs(self, request, queryset):
        for log in queryset:
            if not log.is_approved:
                from . import services
                services.approve_impact_log(log, request.user)
        self.message_user(request, f'{queryset.count()} impact log(s) approved.')
    approve_logs.short_description = 'Approve selected impact logs'


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'hours_threshold']


@admin.register(VolunteerBadge)
class VolunteerBadgeAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'badge', 'awarded_at']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'title', 'issued_at']


@admin.register(CoordinatorMessage)
class CoordinatorMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read']
