import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import services
from .snippe import verify_webhook_signature

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def snippe_webhook(request):
    try:
        raw_body = request.body.decode('utf-8')
    except UnicodeDecodeError:
        return HttpResponseBadRequest('Invalid request encoding')

    if settings.SNIPPE_REQUIRE_WEBHOOK_SIGNATURE and not settings.SNIPPE_WEBHOOK_SECRET:
        logger.error('Rejected Snippe webhook because SNIPPE_WEBHOOK_SECRET is not configured')
        return HttpResponseBadRequest('Webhook verification is unavailable')

    if settings.SNIPPE_WEBHOOK_SECRET:
        try:
            verify_webhook_signature(raw_body, request.headers, settings.SNIPPE_WEBHOOK_SECRET)
        except ValueError:
            logger.warning('Rejected Snippe webhook with invalid signature')
            return HttpResponseBadRequest('Invalid signature')

    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    services.handle_snippe_webhook(event)
    return HttpResponse('OK')
