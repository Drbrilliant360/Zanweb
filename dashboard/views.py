from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Q
from django.utils import timezone
from accounts.models import User, VolunteerProfile
from programs.models import Program, ProgramApplication
from donations.models import Donation
from volunteering.models import EventRegistration, VolunteerBadge, CoordinatorMessage


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def volunteer_dashboard(request):
    vp, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    hours = float(vp.total_impact_hours)
    from volunteering.utils import get_rank_info
    rank_info = get_rank_info(hours)
    upcoming = EventRegistration.objects.filter(
        volunteer=request.user,
    ).exclude(
        status='cancelled',
    ).select_related('event').order_by('event__date')[:5]
    badges = VolunteerBadge.objects.filter(volunteer=request.user).select_related('badge')
    latest_msg = CoordinatorMessage.objects.filter(
        recipient=request.user,
    ).order_by('-created_at').first()
    return Response({
        'greeting_name': request.user.get_full_name() or request.user.email,
        'total_impact_hours': hours,
        'rank': rank_info['rank'],
        'next_rank_threshold_hours': float(vp.next_rank_threshold_hours),
        'percent_to_next_rank': rank_info['percent_to_next_rank'],
        'upcoming_shifts': [
            {
                'event_title': r.event.title,
                'date': r.event.date,
                'start_time': r.event.start_time,
                'end_time': r.event.end_time,
                'location': r.event.location,
            }
            for r in upcoming
        ],
        'recognitions': [
            {
                'badge_name': b.badge.name,
                'icon': b.badge.icon,
                'awarded_at': b.awarded_at,
            }
            for b in badges
        ],
        'latest_coordinator_message': (
            {
                'id': latest_msg.id,
                'sender_name': latest_msg.sender.get_full_name() or latest_msg.sender.email,
                'body': latest_msg.body,
                'created_at': latest_msg.created_at,
            }
            if latest_msg else None
        ),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    total_volunteers = User.objects.filter(role='volunteer', is_active=True).count()
    active_programs = Program.objects.filter(is_published=True, status__in=['active', 'in_progress']).count()
    grants_awarded = Donation.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    recent_applications = ProgramApplication.objects.select_related('program').order_by('-created_at')[:10]
    program_tracking = Program.objects.filter(is_published=True).order_by('-engagement_score')[:10]
    engagement_by_category = Program.objects.filter(is_published=True).values('category').annotate(
        total_engagement=Sum('engagement_score')
    ).order_by('-total_engagement')
    return Response({
        'as_of': timezone.now(),
        'total_volunteers': total_volunteers,
        'active_programs': active_programs,
        'grants_awarded': float(grants_awarded),
        'recent_applications': [
            {
                'id': a.id,
                'applicant_name': a.full_name,
                'email': a.email,
                'program': a.program.name if a.program else None,
                'status': a.status,
                'created_at': a.created_at,
            }
            for a in recent_applications
        ],
        'program_tracking': [
            {
                'id': p.id,
                'name': p.name,
                'coordinator': p.coordinator.get_full_name() if p.coordinator else None,
                'status': p.status,
                'engagement_score': p.engagement_score,
                'budget_total': float(p.budget_total),
                'budget_used': float(p.budget_used),
                'budget_remaining': float(p.budget_remaining),
            }
            for p in program_tracking
        ],
        'engagement_by_category': list(engagement_by_category),
    })
