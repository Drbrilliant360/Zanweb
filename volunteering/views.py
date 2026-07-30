from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from accounts.models import VolunteerProfile
from accounts.permissions import IsAdminRole, IsCoordinatorOrAdmin
from .models import (
    Event, EventRegistration, ImpactLog, Badge,
    VolunteerBadge, Certificate, CoordinatorMessage,
)
from .serializers import (
    EventSerializer, EventRegistrationSerializer, ImpactLogSerializer,
    BadgeSerializer, VolunteerBadgeSerializer, CertificateSerializer,
    CoordinatorMessageSerializer,
)
from . import services
from .utils import get_rank_info


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCoordinatorOrAdmin()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        reg, created = EventRegistration.objects.get_or_create(
            event=event,
            volunteer=request.user,
            defaults={'status': 'registered'},
        )
        if not created and reg.status == 'cancelled':
            reg.status = 'registered'
            reg.save()
        ser = EventRegistrationSerializer(reg)
        return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        try:
            reg = EventRegistration.objects.get(event=event, volunteer=request.user)
        except EventRegistration.DoesNotExist:
            return Response({'detail': 'No registration found.'}, status=status.HTTP_404_NOT_FOUND)
        reg.status = 'cancelled'
        reg.save()
        return Response(EventRegistrationSerializer(reg).data)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.select_related('event', 'volunteer').all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsCoordinatorOrAdmin]

    @action(detail=True, methods=['post'])
    def mark_attended(self, request, pk=None):
        reg = self.get_object()
        hours = request.data.get('hours_logged', 0)
        try:
            hours = int(hours)
        except (TypeError, ValueError):
            return Response({'detail': 'hours_logged must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        services.mark_attendance(reg, hours)
        return Response(EventRegistrationSerializer(reg).data)


class MyEventRegistrationsView(generics.ListAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(
            volunteer=self.request.user,
        ).select_related('event')


class ImpactLogViewSet(viewsets.ModelViewSet):
    serializer_class = ImpactLogSerializer

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [IsCoordinatorOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_admin_role or user.is_coordinator):
            return ImpactLog.objects.select_related('volunteer', 'event').all()
        if user.is_authenticated:
            return ImpactLog.objects.filter(volunteer=user)
        return ImpactLog.objects.none()

    def perform_create(self, serializer):
        serializer.save(volunteer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsCoordinatorOrAdmin])
    def approve(self, request, pk=None):
        log = self.get_object()
        services.approve_impact_log(log, request.user)
        return Response(ImpactLogSerializer(log).data)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]


class MyBadgesView(generics.ListAPIView):
    serializer_class = VolunteerBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VolunteerBadge.objects.filter(volunteer=self.request.user).select_related('badge')


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_admin_role or user.is_coordinator):
            return Certificate.objects.all()
        if user.is_authenticated:
            return Certificate.objects.filter(volunteer=user)
        return Certificate.objects.none()


class CoordinatorMessageViewSet(viewsets.ModelViewSet):
    serializer_class = CoordinatorMessageSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_admin_role or user.is_coordinator):
            return CoordinatorMessage.objects.filter(parent__isnull=True)
        if user.is_authenticated:
            return CoordinatorMessage.objects.filter(
                parent__isnull=True,
            ).filter(
                sender=user,
            ) | CoordinatorMessage.objects.filter(
                parent__isnull=True,
                recipient=user,
            )
        return CoordinatorMessage.objects.none()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        parent = self.get_object()
        recipient = parent.sender if parent.recipient == request.user else parent.recipient
        ser = CoordinatorMessageSerializer(data={
            'recipient': recipient.id,
            'body': request.data.get('body', ''),
            'parent': parent.id,
        }, context=self.get_serializer_context())
        ser.is_valid(raise_exception=True)
        ser.save(sender=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class VolunteerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vp, _ = VolunteerProfile.objects.get_or_create(user=request.user)
        hours = float(vp.total_impact_hours)
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
