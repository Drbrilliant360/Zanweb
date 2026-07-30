from django.db import models
from django.conf import settings


class Event(models.Model):
    program = models.ForeignKey(
        'programs.Program', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='events',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    capacity = models.IntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    @property
    def seats_taken(self):
        return self.registrations.exclude(status='cancelled').count()

    @property
    def seats_remaining(self):
        if self.capacity is None:
            return None
        return self.capacity - self.seats_taken

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    hours_logged = models.IntegerField(default=0)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'volunteer']
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.volunteer.email} — {self.event.title} ({self.status})"


class ImpactLog(models.Model):
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impact_logs',
    )
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='impact_logs',
    )
    hours = models.DecimalField(max_digits=6, decimal_places=1)
    date = models.DateField()
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_impact_logs',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.volunteer.email} — {self.hours}h ({self.date})"


class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, help_text='Emoji character')
    description = models.TextField(blank=True)
    hours_threshold = models.IntegerField(null=True, blank=True, help_text='Auto-awarded above this many hours')

    def __str__(self):
        return self.name


class VolunteerBadge(models.Model):
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='volunteer_badges')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['volunteer', 'badge']

    def __str__(self):
        return f"{self.volunteer.email} — {self.badge.name}"


class Certificate(models.Model):
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    program = models.ForeignKey(
        'programs.Program', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='certificates',
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='certificates/', blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.volunteer.email} — {self.title}"


class CoordinatorMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
    )
    body = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies',
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.email} -> {self.recipient.email}: {self.body[:60]}"
