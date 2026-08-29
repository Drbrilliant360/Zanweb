from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, VolunteerProfile, VolunteerExperience, VolunteerEducation


class VolunteerExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerExperience
        fields = ['id', 'title', 'organization', 'dates', 'description']
        read_only_fields = ['id']


class VolunteerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerEducation
        fields = ['id', 'degree', 'school', 'dates']
        read_only_fields = ['id']


class VolunteerProfileSerializer(serializers.ModelSerializer):
    experiences = VolunteerExperienceSerializer(many=True, required=False)
    education = VolunteerEducationSerializer(many=True, required=False)

    class Meta:
        model = VolunteerProfile
        fields = [
            'id', 'bio', 'skills', 'location', 'country', 'region', 'gender', 'age_group',
            'nationality', 'english_level', 'swahili_level', 'interest_area', 'volunteered_before',
            'total_impact_hours', 'rank', 'next_rank_threshold_hours',
            'is_active_volunteer', 'joined_at', 'experiences', 'education',
        ]
        read_only_fields = ['total_impact_hours', 'rank', 'next_rank_threshold_hours', 'joined_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['experiences'] = VolunteerExperienceSerializer(
            instance.user.experiences.all(), many=True,
        ).data
        data['education'] = VolunteerEducationSerializer(
            instance.user.education_entries.all(), many=True,
        ).data
        return data


class UserSerializer(serializers.ModelSerializer):
    volunteer_profile = VolunteerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'street_address', 'town', 'postal_code',
            'avatar', 'is_active', 'date_joined', 'created_at',
            'accepted_terms', 'accepted_privacy_policy',
            'volunteer_profile',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'is_active', 'date_joined', 'created_at',
            'accepted_terms', 'accepted_privacy_policy',
        ]

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    def _sync_cv_entries(self, user, experiences=None, education=None):
        if experiences is not None:
            user.experiences.all().delete()
            for i, item in enumerate(experiences):
                VolunteerExperience.objects.create(
                    volunteer=user,
                    sort_order=i,
                    **item,
                )
        if education is not None:
            user.education_entries.all().delete()
            for i, item in enumerate(education):
                VolunteerEducation.objects.create(
                    volunteer=user,
                    sort_order=i,
                    **item,
                )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('volunteer_profile', None)
        user = super().update(instance, validated_data)
        if profile_data is None:
            return user

        experiences = profile_data.pop('experiences', None)
        education = profile_data.pop('education', None)
        vp, _ = VolunteerProfile.objects.get_or_create(user=user)
        for attr, val in profile_data.items():
            setattr(vp, attr, val)
        vp.save()
        self._sync_cv_entries(user, experiences, education)
        return user


class PublicVolunteerSerializer(serializers.ModelSerializer):
    """The deliberately small profile returned by the public volunteer directory."""
    full_name = serializers.SerializerMethodField()
    bio = serializers.CharField(source='volunteer_profile.bio', read_only=True)
    skills = serializers.CharField(source='volunteer_profile.skills', read_only=True)
    location = serializers.CharField(source='volunteer_profile.location', read_only=True)
    rank = serializers.CharField(source='volunteer_profile.rank', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'avatar', 'bio', 'skills', 'location', 'rank']

    def get_full_name(self, obj):
        return obj.get_full_name()


class AdminUserSerializer(serializers.ModelSerializer):
    """Account management serializer used only by the protected admin workspace."""
    password = serializers.CharField(write_only=True, min_length=12, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'is_active',
            'is_staff', 'date_joined', 'created_at', 'password',
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'is_staff']

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'A password is required when creating an account.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', 'volunteer')
        user = User.objects.create_user(**validated_data, password=password)
        if role == 'admin':
            user.is_staff = True
            user.save(update_fields=['is_staff'])
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
        # Django-admin access follows the application admin role.
        user.is_staff = user.role == 'admin'
        user.save()
        return user


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False, allow_blank=True)
    street_address = serializers.CharField(required=False, allow_blank=True)
    town = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    age_group = serializers.CharField(required=False, allow_blank=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    english_level = serializers.CharField(required=False, allow_blank=True)
    swahili_level = serializers.CharField(required=False, allow_blank=True)
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
            'country', 'region', 'gender', 'age_group', 'nationality',
            'english_level', 'swahili_level', 'interest_area', 'volunteered_before',
        ]
        profile_kwargs = {k: validated_data.pop(k, '') for k in profile_fields if k != 'volunteered_before'}
        profile_kwargs['volunteered_before'] = validated_data.pop('volunteered_before', None)

        validated_data.pop('password2', None)
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
