from django.contrib import admin
from .models import (
    ContactMessage, NewsletterSubscriber, Partner,
    Story, GalleryImage, FAQ, OrgStat,
)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active']


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_published', 'sort_order']
    list_filter = ['category', 'is_published']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'is_published', 'created_at']
    list_filter = ['is_published']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_at']
    list_filter = ['category']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['topic', 'question_example', 'sort_order', 'is_active']
    list_filter = ['is_active', 'topic']


@admin.register(OrgStat)
class OrgStatAdmin(admin.ModelAdmin):
    list_display = ['label', 'value', 'order']
