from django.db.models import Sum
from .models import ImpactLog, VolunteerBadge, Badge


def _award_eligible_badges(volunteer):
    total = ImpactLog.objects.filter(volunteer=volunteer, is_approved=True).aggregate(
        total=Sum('hours')
    )['total'] or 0
    total = float(total)
    eligible = Badge.objects.filter(
        hours_threshold__isnull=False,
        hours_threshold__lte=total,
    ).exclude(volunteer_badges__volunteer=volunteer)
    for badge in eligible:
        VolunteerBadge.objects.get_or_create(volunteer=volunteer, badge=badge)


def recompute_volunteer_stats(volunteer):
    total = ImpactLog.objects.filter(volunteer=volunteer, is_approved=True).aggregate(
        total=Sum('hours')
    )['total'] or 0
    vp = volunteer.volunteer_profile
    if vp:
        vp.total_impact_hours = total
        vp.save()
        vp.recompute_rank()
    _award_eligible_badges(volunteer)


def approve_impact_log(log, approver):
    log.is_approved = True
    log.approved_by = approver
    import django.utils.timezone as tz
    log.approved_at = tz.now()
    log.save()
    recompute_volunteer_stats(log.volunteer)


def mark_attendance(registration, hours):
    registration.status = 'attended'
    registration.hours_logged = hours
    registration.save()
    log, _ = ImpactLog.objects.update_or_create(
        volunteer=registration.volunteer,
        event=registration.event,
        defaults={
            'hours': hours,
            'date': registration.event.date,
            'description': f'Attendance for {registration.event.title}',
        },
    )
    approve_impact_log(log, registration.event.coordinator if hasattr(registration.event, 'coordinator') and registration.event.coordinator else None)
