from rest_framework import viewsets, permissions, status, throttling
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import mail_admins
from accounts.permissions import IsCoordinatorOrAdminOrReadOnly
import requests
import urllib.parse
from .models import (
    ContactMessage, NewsletterSubscriber, Partner,
    Story, GalleryImage, FAQ, OrgStat, SiteContent,
)
from .serializers import (
    ContactMessageSerializer,
    NewsletterSubscriberSerializer,
    PartnerSerializer,
    StorySerializer,
    GalleryImageSerializer,
    FAQSerializer,
    OrgStatSerializer,
    SiteContentSerializer,
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


class SiteContentView(APIView):
    """Persist all admin CMS data (hero, mission, priorities, etc.) to DB.
    GET is public (for future public pages), PUT/PATCH requires admin."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request, key='zcm_admin_data_v1'):
        obj, _ = SiteContent.objects.get_or_create(key=key, defaults={'data': {}})
        ser = SiteContentSerializer(obj)
        return Response(ser.data)

    def put(self, request, key='zcm_admin_data_v1'):
        obj, _ = SiteContent.objects.get_or_create(key=key, defaults={'data': {}})
        # Accept either {data: {...}} or raw {...}
        incoming = request.data.get('data') if isinstance(request.data.get('data'), dict) else request.data
        if not isinstance(incoming, dict):
            return Response({'detail': 'data must be an object'}, status=status.HTTP_400_BAD_REQUEST)
        obj.data = incoming
        obj.updated_by = request.user if request.user.is_authenticated else None
        obj.save()
        return Response(SiteContentSerializer(obj).data)

    def patch(self, request, key='zcm_admin_data_v1'):
        return self.put(request, key)


# Free online model proxy — Pollinations AI (no API key, OpenAI-compatible)
# Found via https://text.pollinations.ai — free, anonymous tier, Mistral/Llama backing
class ChatbotProxyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'chatbot'
    # Tanzanian context injected so free model answers as Zanchangemakers assistant
    SYSTEM_PROMPT = (
        "You are Zanchangemakers Support — a friendly assistant for Zanchangemakers, "
        "a youth volunteer movement based in Zanzibar, Tanzania. "
        "You help with: programs (Youth Volunteers Forum, career placements), "
        "volunteering, donations (TZS via mobile money PBZ bank), contact info "
        "(+255 777 426 972, info@zanchangemakers.co.tz, Zanzibar). "
        "Answer concisely, warmly, in English or Swahili as the user prefers. "
        "If unsure, invite them to visit /contact/ or call. Keep replies under 90 words."
    )

    def post(self, request):
        msg = (request.data.get('message') or request.data.get('prompt') or '').strip()
        if not msg:
            msg = (request.query_params.get('q') or '').strip()
        if not msg:
            return Response({'detail': 'message is required'}, status=status.HTTP_400_BAD_REQUEST)
        if len(msg) > 500:
            return Response({'detail': 'message must be 500 characters or fewer'}, status=status.HTTP_400_BAD_REQUEST)
        # First try FAQ quick match for speed
        # Then try free online model
        import time as _time
        try:
            # Try lightweight GET first (fast, free, no key) — just the user message with short Zanzibar context
            enc_simple = urllib.parse.quote(msg, safe="")
            g = requests.get(f"https://text.pollinations.ai/{enc_simple}", timeout=10)
            if g.status_code == 429:
                _time.sleep(1.5)
                g = requests.get(f"https://text.pollinations.ai/{enc_simple}", timeout=10)
            if g.ok and g.text.strip():
                txt = g.text.strip()
                if not txt.lower().startswith("<!doctype") and "queue full" not in txt.lower() and len(txt) >= 1:
                    return Response({"reply": txt[:1200], "model": "pollinations-free", "source": "pollinations.ai (free online)"})
            # Fallback: OpenAI-compatible endpoint with system prompt (better for Zanchangemakers context)
            poll_url = "https://text.pollinations.ai/openai"
            payload = {
                "model": "openai",
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.7,
                "max_tokens": 280,
            }
            r = requests.post(poll_url, json=payload, timeout=12, headers={"Content-Type": "application/json"})
            if r.status_code == 429:
                _time.sleep(1.5)
                r = requests.post(poll_url, json=payload, timeout=12, headers={"Content-Type": "application/json"})
            if r.ok:
                try:
                    j = r.json()
                except Exception:
                    j = {}
                reply = ""
                try:
                    reply = j["choices"][0]["message"]["content"].strip()
                except Exception:
                    reply = j.get("choices", [{}])[0].get("message", {}).get("content", "") or r.text.strip()
                if reply and "queue full" not in reply.lower():
                    return Response({
                        "reply": reply,
                        "model": j.get("model", "pollinations-free"),
                        "source": "pollinations.ai (free online)",
                    })
        except Exception as e:
            # network failure → fallback to local FAQ
            pass
        # Fallback: local FAQ match
        qlow = msg.lower()
        best = None
        best_score = 0
        for entry in FAQ.objects.filter(is_active=True):
            score = sum(1 for kw in entry.keyword_list if kw.lower() in qlow)
            if score > best_score:
                best_score = score
                best = entry
        if best and best_score > 0:
            return Response({"reply": best.answer, "model": "local-faq", "source": "offline fallback"})
        # Last resort: helpful generic answer that still acknowledges the query (covers “all queries” when free model is rate-limited)
        # This keeps chatbot responsive even when pollinations.ai queue is full
        low = msg.lower()
        # Tailor fallback by intent for better UX
        if any(k in low for k in ["hello","hi","hey","jambo","habari"]):
            fb = "Hello! 👋 Karibu Zanchangemakers! Ask me anything — programs, volunteering, donations (TZS), or just chat. How can I help today?"
        elif "tanzania" in low or "zanzibar" in low:
            fb = (
                f"You asked: “{msg}” — Zanchangemakers is a Zanzibar-based youth movement since 2021, "
                "running the Youth Volunteers Forum (YVF) and career placement cohorts across Tanzania. "
                "We’d love you to volunteer via /volunteer/ or donate TZS via PBZ (0836881001) / Mix by Yas (44348982). "
                "Reach us at +255 777 426 972 or info@zanchangemakers.co.tz."
            )
        else:
            fb = (
                f"Thanks for asking: “{msg}”\n\n"
                "I’m Zanchangemakers Support (free AI via pollinations.ai when online, offline fallback otherwise). "
                "We empower youth through volunteerism & skills in Zanzibar/Tanzania. I can help with:\n"
                "• Programs: YVF, career placements — see /programs/\n"
                "• Volunteering: join via /volunteer/\n"
                "• Donations: TZS via PBZ 0836881001 or Mix by Yas 44348982 — /donate/\n"
                "• Contact: +255 777 426 972, info@zanchangemakers.co.tz, /contact/\n\n"
                "Feel free to rephrase or ask anything — I’ll do my best to answer!"
            )
        return Response({
            "reply": fb,
            "model": "local-fallback",
            "source": "offline fallback (pollinations.ai busy, answering locally)",
        })

    def get(self, request):
        # Allow GET ?q=hello for easy browser testing
        request.data = {"message": request.query_params.get("q", "")}
        return self.post(request)
