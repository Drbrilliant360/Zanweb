from django.contrib import admin
from .models import Program, Cohort, ProgramApplication


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'is_published', 'created_at']
    list_filter = ['category', 'status', 'is_published']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'number', 'is_accepting_applications']
    list_filter = ['is_accepting_applications']


@admin.register(ProgramApplication)
class ProgramApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'program', 'status', 'created_at']
    list_filter = ['status', 'request_type']
    search_fields = ['full_name', 'email']
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        queryset.update(status='approved')
    approve_applications.short_description = 'Approve selected applications'

    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')
    reject_applications.short_description = 'Reject selected applications'
