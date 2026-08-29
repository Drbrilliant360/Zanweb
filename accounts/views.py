from rest_framework import generics, permissions, status, throttling, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .models import User, VolunteerProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    VolunteerProfileSerializer,
    PublicVolunteerSerializer,
    AdminUserSerializer,
)
from .permissions import IsAdminRole
from .permissions import IsAdminRole


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {'user': UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request):
        ser = LoginSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response(
            {'user': UserSerializer(user).data, **tokens},
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': 'Logged out successfully.'})
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return User.objects.select_related('volunteer_profile').prefetch_related(
            'experiences', 'education_entries',
        ).get(pk=self.request.user.pk)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        request.user.set_password(ser.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})


class VolunteerListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicVolunteerSerializer

    def get_queryset(self):
        qs = User.objects.filter(role='volunteer', is_active=True,
                                 volunteer_profile__is_active_volunteer=True)
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(volunteer_profile__location__icontains=search) |
                Q(volunteer_profile__skills__icontains=search)
            )
        return qs


class VolunteerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.filter(role='volunteer')
    serializer_class = UserSerializer


class AdminUserViewSet(viewsets.ModelViewSet):
    """Safe account management for the custom admin workspace."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]

    def perform_destroy(self, instance):
        if instance == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'You cannot delete your own account.'})
        if instance.role == 'admin' and User.objects.filter(role='admin', is_active=True).count() <= 1:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'At least one active administrator must remain.'})
        instance.delete()
