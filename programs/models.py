from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Program(models.Model):
    CATEGORY_CHOICES = [
        ('leadership_volunteerism', 'Leadership & Volunteerism'),
        ('career_readiness', 'Career Readiness'),
        ('community_impact', 'Community Impact'),
        ('digital_skills', 'Digital Skills'),
        ('health_wellbeing', 'Health & Wellbeing'),
    ]
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='program_covers/', blank=True, null=True)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='coordinated_programs',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    engagement_score = models.IntegerField(default=0, help_text='0–100')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def budget_remaining(self):
        return self.budget_total - self.budget_used

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Cohort(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='cohorts')
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_accepting_applications = models.BooleanField(default=True)

    class Meta:
        unique_together = ['program', 'number']
        ordering = ['program', 'number']

    def __str__(self):
        return f'{self.program.name} — Cohort {self.number}: {self.name}'


class ProgramApplication(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('volunteer', 'Volunteer'),
        ('internship', 'Internship'),
        ('professional', 'Professional'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='volunteer')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, blank=True, null=True, related_name='applications')
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, blank=True, null=True, related_name='applications')
    message = models.TextField(blank=True)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='program_applications',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='reviewed_applications',
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.status}'
