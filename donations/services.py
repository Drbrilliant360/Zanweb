from django.conf import settings
from django.db.models import F
from django.utils import timezone

from .models import DonationCampaign
from .snippe import SnippeError, create_mobile_payment, split_name


def initiate_payment(donation):
    if donation.method == 'mobile_money' and settings.PAYMENT_GATEWAY_PROVIDER == 'snippe':
        return initiate_snippe_payment(donation)

    if donation.method == 'bank_transfer':
        return {
            'bank_name': 'People\'s Bank of Zanzibar (PBZ)',
            'account_name': 'Zanchangemakers Initiative',
            'account_number': '040001234567',
            'branch': 'Zanzibar Main Branch',
            'swift_bic': 'PBZATZTZXXX',
            'reference': f'DON-{donation.id}',
        }
    if donation.method == 'mobile_money':
        return {
            'provider': 'manual',
            'reference': f'DON-{donation.id}',
            'message': 'Mobile money USSD push is not configured. Contact support to complete your donation.',
        }
    if donation.method == 'card':
        return {
            'instructions': 'Card payments are not yet processed. Please use mobile money or bank transfer.',
        }
    return {}


def initiate_snippe_payment(donation):
    first, last = split_name(donation.donor_name)
    amount = int(donation.amount)
    if amount < 500:
        raise SnippeError('Minimum mobile money donation is 500 TZS')

    webhook_url = f"{settings.SITE_BASE_URL.rstrip('/')}/api/webhooks/snippe/"
    email = donation.donor_email or f'donor-{donation.id}@zanchangemakers.local'

    try:
        result = create_mobile_payment(
            amount=amount,
            phone_number=donation.donor_phone,
            customer={
                'firstname': first,
                'lastname': last,
                'email': email,
            },
            webhook_url=webhook_url,
            metadata={'donation_id': str(donation.id)},
            idempotency_key=f'don-{donation.id}',
        )
    except SnippeError as exc:
        fail_payment(donation, str(exc))
        raise

    donation.transaction_reference = result.get('reference', '')
    donation.currency = 'TZS'
    donation.save(update_fields=['transaction_reference', 'currency'])

    return {
        'provider': 'snippe',
        'reference': result.get('reference'),
        'status': result.get('status', 'pending'),
        'expires_at': result.get('expires_at'),
        'message': (
            'A USSD payment prompt has been sent to your phone. '
            'Enter your mobile money PIN to authorize the payment.'
        ),
        'phone_number': donation.donor_phone,
    }


def confirm_payment(donation, transaction_reference):
    if donation.status == 'completed':
        return

    donation.status = 'completed'
    donation.transaction_reference = transaction_reference or donation.transaction_reference
    donation.completed_at = timezone.now()
    donation.save()

    if donation.campaign_id:
        DonationCampaign.objects.filter(pk=donation.campaign_id).update(
            raised_amount=F('raised_amount') + donation.amount,
        )


def fail_payment(donation, reason):
    donation.status = 'failed'
    if donation.message:
        donation.message += f'\nFailure reason: {reason}'
    else:
        donation.message = f'Failure reason: {reason}'
    donation.save()


def handle_snippe_webhook(event):
    event_type = event.get('type', '')
    data = event.get('data', {})
    donation = _find_donation_from_event(data)
    if not donation:
        return

    reference = data.get('reference') or data.get('external_reference') or ''
    if event_type == 'payment.completed':
        confirm_payment(donation, reference)
    elif event_type in ('payment.failed', 'payment.expired', 'payment.voided'):
        reason = data.get('failure_reason') or event_type.replace('payment.', '')
        fail_payment(donation, reason)


def _find_donation_from_event(data):
    from .models import Donation

    metadata = data.get('metadata') or {}
    donation_id = metadata.get('donation_id')
    if donation_id:
        return Donation.objects.filter(pk=donation_id).first()

    reference = data.get('reference')
    if reference:
        return Donation.objects.filter(transaction_reference=reference).first()
    return None
