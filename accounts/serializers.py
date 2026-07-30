from rest_framework import serializers
from django.contrib.auth import authenticate
from django.conf import settings
from .models import User, VolunteerProfile


class VolunteerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = [
            'id', 'bio', 'skills', 'location', 'region', 'gender', 'age_group',
            'nationality', 'english_level', 'interest_area', 'volunteered_before',
            'total_impact_hours', 'rank', 'next_rank_threshold_hours',
            'is_active_volunteer', 'joined_at',
        ]
        read_only_fields = ['total_impact_hours', 'rank', 'next_rank_threshold_hours', 'joined_at']


class UserSerializer(serializers.ModelSerializer):
    volunteer_profile = VolunteerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'street_address', 'town', 'postal_code',
            'avatar', 'is_active', 'date_joined', 'created_at',
            'volunteer_profile',
        ]
        read_only_fields = ['id', 'is_active', 'date_joined', 'created_at']

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False, allow_blank=True)
    street_address = serializers.CharField(required=False, allow_blank=True)
    town = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    age_group = serializers.CharField(required=False, allow_blank=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    english_level = serializers.CharField(required=False, allow_blank=True)
    interest_area = serializers.CharField(required=False, allow_blank=True)
    volunteered_before = serializers.BooleanField(required=False, allow_null=True, default=None)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    accepted_terms = serializers.BooleanField(required=True)
    accepted_privacy_policy = serializers.BooleanField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        if not data.get('accepted_terms'):
            raise serializers.ValidationError({'accepted_terms': 'You must accept the terms.'})
        if not data.get('accepted_privacy_policy'):
            raise serializers.ValidationError({'accepted_privacy_policy': 'You must accept the privacy policy.'})
        return data

    def create(self, validated_data):
        profile_fields = [
            'region', 'gender', 'age_group', 'nationality',
            'english_level', 'interest_area', 'volunteered_before',
        ]
        profile_kwargs = {k: validated_data.pop(k, '') for k in profile_fields}
        profile_kwargs['volunteered_before'] = validated_data.pop('volunteered_before', None)

        validated_data.pop('password2', None)
        validated_data.pop('accepted_terms', None)
        validated_data.pop('accepted_privacy_policy', None)

        password = validated_data.pop('password')
        validated_data['role'] = 'volunteer'
        user = User.objects.create_user(**validated_data, password=password)

        vp, _ = VolunteerProfile.objects.get_or_create(user=user)
        for attr, val in profile_kwargs.items():
            if val is not None and val != '':
                setattr(vp, attr, val)
        vp.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(request=self.context.get('request'), username=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid email or password.')
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
