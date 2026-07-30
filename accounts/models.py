from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ('volunteer', 'Volunteer'),
        ('coordinator', 'Coordinator'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')
    phone_number = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    accepted_terms = models.BooleanField(default=False)
    accepted_privacy_policy = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-date_joined']

    @property
    def is_volunteer(self):
        return self.role == 'volunteer'

    @property
    def is_coordinator(self):
        return self.role == 'coordinator'

    @property
    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        return self.email


class VolunteerProfile(models.Model):
    REGION_CHOICES = [
        ('zanzibar_north', 'Zanzibar North'),
        ('zanzibar_south', 'Zanzibar South'),
        ('zanzibar_urban_west', 'Zanzibar Urban West'),
        ('dar_es_salaam', 'Dar es Salaam'),
        ('pemba_north', 'Pemba North'),
        ('pemba_south', 'Pemba South'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    AGE_GROUP_CHOICES = [
        ('16_18', '16-18'),
        ('19_25', '19-25'),
        ('26_35', '26-35'),
        ('36_plus', '36+'),
    ]
    NATIONALITY_CHOICES = [
        ('tanzanian', 'Tanzanian'),
        ('kenyan', 'Kenyan'),
        ('ugandan', 'Ugandan'),
        ('other', 'Other'),
    ]
    ENGLISH_LEVEL_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('fluent', 'Fluent'),
    ]
    INTEREST_CHOICES = [
        ('community_development', 'Community Development'),
        ('youth_mentorship', 'Youth Mentorship'),
        ('environmental_action', 'Environmental Action'),
        ('digital_skills', 'Digital Skills Training'),
    ]
    RANK_CHOICES = [
        ('newcomer', 'Newcomer'),
        ('active', 'Active'),
        ('elite', 'Elite'),
        ('platinum', 'Platinum'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
    )
    bio = models.TextField(max_length=1000, blank=True)
    skills = models.CharField(max_length=500, blank=True, help_text='Comma-separated skills')
    location = models.CharField(max_length=200, blank=True)
    region = models.CharField(max_length=30, choices=REGION_CHOICES, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, blank=True)
    nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES, blank=True)
    english_level = models.CharField(max_length=20, choices=ENGLISH_LEVEL_CHOICES, blank=True)
    interest_area = models.CharField(max_length=30, choices=INTEREST_CHOICES, blank=True)
    volunteered_before = models.BooleanField(null=True, blank=True)
    total_impact_hours = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='newcomer')
    next_rank_threshold_hours = models.DecimalField(max_digits=8, decimal_places=1, default=40)
    is_active_volunteer = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def recompute_rank(self):
        hours = float(self.total_impact_hours)
        if hours < 40:
            self.rank = 'newcomer'
            self.next_rank_threshold_hours = 40
        elif hours < 100:
            self.rank = 'active'
            self.next_rank_threshold_hours = 100
        elif hours < 140:
            self.rank = 'elite'
            self.next_rank_threshold_hours = 140
        else:
            self.rank = 'platinum'
            self.next_rank_threshold_hours = 140
        self.save(update_fields=['rank', 'next_rank_threshold_hours'])

    def __str__(self):
        return f'{self.user.email} — {self.rank}'
