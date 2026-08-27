import hashlib
import hmac
import time
import uuid

import requests
from django.conf import settings


class SnippeError(Exception):
    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


def _headers(idempotency_key=None):
    headers = {
        'Authorization': f'Bearer {settings.SNIPPE_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    api_version = getattr(settings, 'SNIPPE_API_VERSION', '')
    if api_version:
        headers['Snippe-Version'] = api_version
    if idempotency_key:
        headers['Idempotency-Key'] = idempotency_key[:30]
    return headers


def _api_url(path):
    return f'{settings.SNIPPE_API_BASE_URL.rstrip("/")}{path}'


def _parse_response(response):
    try:
        payload = response.json()
    except ValueError as exc:
        raise SnippeError(
            f'Snippe returned invalid JSON (HTTP {response.status_code})',
            status_code=response.status_code,
        ) from exc

    if payload.get('status') == 'error' or response.status_code >= 400:
        raise SnippeError(
            payload.get('message', 'Snippe payment request failed'),
            status_code=payload.get('code', response.status_code),
            error_code=payload.get('error_code'),
        )
    return payload.get('data', payload)


def normalize_phone(phone):
    phone = (phone or '').strip().replace(' ', '').replace('-', '')
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('0'):
        phone = '255' + phone[1:]
    if not phone.startswith('255'):
        phone = '255' + phone
    return phone


def split_name(full_name):
    parts = (full_name or 'Donor').strip().split(None, 1)
    first = parts[0] if parts else 'Donor'
    last = parts[1] if len(parts) > 1 else 'Donor'
    return first, last


def resolve_snippe_webhook_url():
    """Return HTTPS webhook URL from SNIPPE_WEBHOOK_URL or SITE_BASE_URL."""
    explicit = (getattr(settings, 'SNIPPE_WEBHOOK_URL', '') or '').strip()
    if explicit:
        url = explicit
    else:
        base = (getattr(settings, 'SITE_BASE_URL', '') or '').rstrip('/')
        url = f'{base}/api/webhooks/snippe/' if base else ''

    if url.startswith('https://') and len(url) <= 500:
        return url
    return None


def require_snippe_webhook_url():
    """Snippe requires webhook_url (HTTPS). VAL_001 if missing or not HTTPS."""
    url = resolve_snippe_webhook_url()
    if url:
        return url
    raise SnippeError(
        'webhook_url is required and must use HTTPS (VAL_001). '
        'Set SNIPPE_WEBHOOK_URL=https://your-domain.com/api/webhooks/snippe/ '
        'and register it in Snippe Dashboard → Webhooks with payment.completed enabled. '
        'For local testing: run "ngrok http 8000" and use the https ngrok URL.',
        error_code='VAL_001',
    )


def create_mobile_payment(
    *,
    amount,
    phone_number,
    customer,
    webhook_url,
    metadata=None,
    idempotency_key=None,
):
    if not settings.SNIPPE_API_KEY:
        raise SnippeError('SNIPPE_API_KEY is not configured')
    if not webhook_url or not webhook_url.startswith('https://'):
        raise SnippeError(
            'webhook_url is required and must use HTTPS (VAL_001)',
            error_code='VAL_001',
        )

    body = {
        'payment_type': 'mobile',
        'details': {
            'amount': int(amount),
            'currency': 'TZS',
        },
        'phone_number': normalize_phone(phone_number),
        'customer': {
            'firstname': customer['firstname'],
            'lastname': customer['lastname'],
            'email': customer['email'],
        },
        'webhook_url': webhook_url,
        'metadata': metadata or {},
    }

    response = requests.post(
        _api_url('/v1/payments'),
        headers=_headers(idempotency_key or uuid.uuid4().hex[:30]),
        json=body,
        timeout=30,
    )
    return _parse_response(response)


def get_payment_status(reference):
    if not settings.SNIPPE_API_KEY:
        raise SnippeError('SNIPPE_API_KEY is not configured')

    response = requests.get(
        _api_url(f'/v1/payments/{reference}'),
        headers=_headers(),
        timeout=30,
    )
    return _parse_response(response)


def verify_webhook_signature(raw_body, headers, signing_key):
    if not signing_key:
        raise ValueError('SNIPPE_WEBHOOK_SECRET is not configured')

    timestamp = headers.get('X-Webhook-Timestamp') or headers.get('x-webhook-timestamp')
    signature = headers.get('X-Webhook-Signature') or headers.get('x-webhook-signature')

    if not timestamp or not signature:
        raise ValueError('Missing webhook signature headers')

    event_time = int(timestamp)
    if abs(int(time.time()) - event_time) > 300:
        raise ValueError('Webhook timestamp too old')

    message = f'{timestamp}.{raw_body}'
    expected = hmac.new(
        signing_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise ValueError('Invalid webhook signature')
