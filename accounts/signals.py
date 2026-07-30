from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import VolunteerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_volunteer_profile(sender, instance, created, **kwargs):
    if created:
        VolunteerProfile.objects.get_or_create(user=instance)
