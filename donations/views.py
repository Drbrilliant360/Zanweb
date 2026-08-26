from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdminRole, IsCoordinatorOrAdminOrReadOnly
from .models import DonationCampaign, DonationTier, Donation
from .serializers import (
    DonationCampaignSerializer,
    DonationTierSerializer,
    DonationSerializer,
    ConfirmDonationSerializer,
)
from .snippe import SnippeError
from . import services


class DonationCampaignViewSet(viewsets.ModelViewSet):
    queryset = DonationCampaign.objects.all()
    serializer_class = DonationCampaignSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]

    def get_queryset(self):
        if self.request.method in permissions.SAFE_METHODS:
            return DonationCampaign.objects.filter(is_active=True)
        return DonationCampaign.objects.all()


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def perform_create(self, serializer):
        donation = serializer.save()
        payment_instructions = services.initiate_payment(donation)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        donation = ser.save()
        try:
            payment_instructions = services.initiate_payment(donation)
        except SnippeError as exc:
            return Response(
                {'detail': str(exc), 'error_code': exc.error_code},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({
            'donation': DonationSerializer(donation, context=self.get_serializer_context()).data,
            'payment_instructions': payment_instructions,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def confirm(self, request, pk=None):
        donation = self.get_object()
        confirm_ser = ConfirmDonationSerializer(data=request.data)
        confirm_ser.is_valid(raise_exception=True)
        services.confirm_payment(donation, confirm_ser.validated_data['transaction_reference'])
        return Response(DonationSerializer(donation).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def mark_failed(self, request, pk=None):
        donation = self.get_object()
        reason = request.data.get('reason', 'Marked as failed by admin.')
        services.fail_payment(donation, reason)
        return Response(DonationSerializer(donation).data)
