from rest_framework import serializers
from .models import (
    Event, EventRegistration, ImpactLog, Badge,
    VolunteerBadge, Certificate, CoordinatorMessage,
)


class EventSerializer(serializers.ModelSerializer):
    seats_taken = serializers.ReadOnlyField()
    seats_remaining = serializers.ReadOnlyField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.registrations.filter(
                volunteer=request.user,
            ).exclude(status='cancelled').exists()
        return False


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['status', 'hours_logged', 'registered_at']


class ImpactLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactLog
        fields = '__all__'
        read_only_fields = ['volunteer', 'is_approved', 'approved_by', 'approved_at', 'created_at']


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'


class VolunteerBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = VolunteerBadge
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ['issued_at']


class CoordinatorMessageSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CoordinatorMessage
        fields = '__all__'
        read_only_fields = ['sender', 'is_read', 'created_at']

    def get_replies(self, obj):
        if obj.parent is not None:
            return []
        qs = CoordinatorMessage.objects.filter(parent=obj)
        return CoordinatorMessageSerializer(qs, many=True, context=self.context).data
