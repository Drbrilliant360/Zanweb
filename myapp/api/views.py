from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from myapp.models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        profile_data = {
            'phone_number': request.data.get('phone_number', ''),
            'location': request.data.get('location', 'Zanzibar, Tanzania'),
            'bio': request.data.get('bio', ''),
        }
        UserProfile.objects.create(user=user, **profile_data)

        return Response(
            {'detail': 'User registered successfully', 'user_id': user.id},
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
