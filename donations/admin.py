from django.contrib import admin
from .models import DonationCampaign, DonationTier, Donation


@admin.register(DonationCampaign)
class DonationCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal_amount', 'raised_amount', 'is_active', 'percent_achieved']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(DonationTier)
class DonationTierAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'name', 'amount', 'sort_order']
    list_filter = ['campaign']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['donor_name', 'donor_email']
    actions = ['confirm_donations']

    def confirm_donations(self, request, queryset):
        for donation in queryset:
            if donation.status != 'completed':
                from django.utils import timezone
                donation.status = 'completed'
                donation.completed_at = timezone.now()
                donation.save()
        self.message_user(request, f'{queryset.count()} donation(s) confirmed.')
    confirm_donations.short_description = 'Mark selected as completed'
