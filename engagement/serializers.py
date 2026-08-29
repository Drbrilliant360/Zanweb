from rest_framework import serializers
from .models import (
    ContactMessage, NewsletterSubscriber, Partner,
    Story, GalleryImage, FAQ, OrgStat, SiteContent,
)


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['is_read', 'created_at']


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = '__all__'
        read_only_fields = ['subscribed_at']


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'
        read_only_fields = ['created_at']


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'
        read_only_fields = ['uploaded_at']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class OrgStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgStat
        fields = '__all__'


class SiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContent
        fields = ['id', 'key', 'data', 'updated_at', 'updated_by']
        read_only_fields = ['id', 'updated_at', 'updated_by']
