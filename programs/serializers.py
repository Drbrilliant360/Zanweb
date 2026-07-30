from rest_framework import serializers
from django.db.models import Count
from .models import Program, Cohort, ProgramApplication


class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = '__all__'


class ProgramListSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.SerializerMethodField()
    budget_remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    applications_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'name', 'slug', 'category', 'short_description',
            'cover_image', 'coordinator_name', 'status',
            'budget_total', 'budget_used', 'budget_remaining',
            'engagement_score', 'is_published', 'applications_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_coordinator_name(self, obj):
        if obj.coordinator:
            return obj.coordinator.get_full_name() or obj.coordinator.email
        return None


class ProgramDetailSerializer(serializers.ModelSerializer):
    cohorts = CohortSerializer(many=True, read_only=True)
    coordinator_name = serializers.SerializerMethodField()
    budget_remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    applications_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_coordinator_name(self, obj):
        if obj.coordinator:
            return obj.coordinator.get_full_name() or obj.coordinator.email
        return None


class ProgramApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramApplication
        fields = '__all__'
        read_only_fields = ['status', 'reviewed_by', 'reviewed_at', 'review_notes', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data.setdefault('applicant', request.user)
        return super().create(validated_data)


class ProgramApplicationReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approved', 'rejected'])
    review_notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, application, reviewer):
        application.status = self.validated_data['decision']
        application.reviewed_by = reviewer
        application.review_notes = self.validated_data.get('review_notes', '')
        application.save()
        return application
