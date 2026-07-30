from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from .models import Program, Cohort, ProgramApplication
from .serializers import (
    ProgramListSerializer,
    ProgramDetailSerializer,
    CohortSerializer,
    ProgramApplicationSerializer,
    ProgramApplicationReviewSerializer,
)
from accounts.permissions import IsCoordinatorOrAdmin, IsCoordinatorOrAdminOrReadOnly


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.annotate(
        applications_count=Count('applications')
    ).select_related('coordinator').prefetch_related('cohorts')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramListSerializer
        return ProgramDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsCoordinatorOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (user.is_admin_role or user.is_coordinator):
            return qs
        return qs.filter(is_published=True)


class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]


class ProgramApplicationViewSet(viewsets.ModelViewSet):
    queryset = ProgramApplication.objects.select_related('program', 'cohort', 'applicant', 'reviewed_by')
    serializer_class = ProgramApplicationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsCoordinatorOrAdmin()]

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        application = self.get_object()
        ser = ProgramApplicationReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(application=application, reviewer=request.user)
        return Response(ProgramApplicationSerializer(application).data)
