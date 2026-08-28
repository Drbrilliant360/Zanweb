from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Sum


class DonationCampaign(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='TZS')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def percent_achieved(self):
        if self.goal_amount and self.goal_amount > 0:
            pct = (float(self.raised_amount) / float(self.goal_amount)) * 100
            return min(pct, 100)
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class DonationTier(models.Model):
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, related_name='tiers')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'amount']

    def __str__(self):
        return f"{self.campaign.title} — {self.name}"


class Donation(models.Model):
    METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
    ]
    MOBILE_PROVIDER_CHOICES = [
        ('ezypesa', 'EzyPesa'),
        ('airtel_money', 'Airtel Money'),
        ('mpesa', 'M-Pesa'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.SET_NULL, blank=True, null=True, related_name='donations')
    donor_name = models.CharField(max_length=200, blank=True)
    donor_email = models.EmailField(blank=True)
    donor_phone = models.CharField(max_length=20, blank=True)
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='donations',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TZS')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    mobile_provider = models.CharField(max_length=20, choices=MOBILE_PROVIDER_CHOICES, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.donor_name} — {self.amount} ({self.method})"
