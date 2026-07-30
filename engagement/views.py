from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import mail_admins
from accounts.permissions import IsCoordinatorOrAdminOrReadOnly
from .models import (
    ContactMessage, NewsletterSubscriber, Partner,
    Story, GalleryImage, FAQ, OrgStat,
)
from .serializers import (
    ContactMessageSerializer,
    NewsletterSubscriberSerializer,
    PartnerSerializer,
    StorySerializer,
    GalleryImageSerializer,
    FAQSerializer,
    OrgStatSerializer,
)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        msg = serializer.save()
        try:
            mail_admins(
                subject=f'New contact message: {msg.subject}',
                message=f'From: {msg.name} ({msg.email})\n\n{msg.message}',
                fail_silently=True,
            )
        except Exception:
            pass

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def mark_read(self, request, pk=None):
        msg = self.get_object()
        msg.is_read = True
        msg.save()
        return Response({'status': 'marked as read'})


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        sub, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True},
        )
        if not created and not sub.is_active:
            sub.is_active = True
            sub.save()
        ser = self.get_serializer(sub)
        return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]

    def get_queryset(self):
        if self.request.method in permissions.SAFE_METHODS:
            return Partner.objects.filter(is_published=True)
        return Partner.objects.all()


class StoryViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]

    def get_queryset(self):
        if self.request.method in permissions.SAFE_METHODS:
            return Story.objects.filter(is_published=True)
        return Story.objects.all()


class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]


class OrgStatViewSet(viewsets.ModelViewSet):
    queryset = OrgStat.objects.all()
    serializer_class = OrgStatSerializer
    permission_classes = [IsCoordinatorOrAdminOrReadOnly]


class FAQMatchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').lower()
        entries = FAQ.objects.filter(is_active=True)
        if not q:
            return Response({'answer': None, 'topic': None})

        best_entry = None
        best_score = 0
        for entry in entries:
            score = 0
            for kw in entry.keyword_list:
                if kw.lower() in q:
                    score += 1
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score > 0:
            return Response({
                'answer': best_entry.answer,
                'topic': best_entry.topic or best_entry.question_example,
                'question': best_entry.question_example or best_entry.question,
            })
        return Response({
            'answer': 'I can answer questions about our programs, volunteering, donations, and contact information. Try rephrasing your question!',
            'topic': 'No specific match',
            'question': None,
        })
