from django.conf import settings
from django.utils import timezone


def initiate_payment(donation):
    provider = getattr(settings, 'PAYMENT_GATEWAY_PROVIDER', 'manual')
    if provider != 'manual':
        raise NotImplementedError(
            f"Real payment gateway ({provider}) not yet integrated. "
            "Implement the SDK call here, then call confirm_payment() on success."
        )
    if donation.method == 'bank_transfer':
        return {
            'bank_name': 'People\'s Bank of Zanzibar (PBZ)',
            'account_name': 'Zanchangemakers Initiative',
            'account_number': '040001234567',
            'branch': 'Zanzibar Main Branch',
            'swift_bic': 'PBZATZTZXXX',
            'reference': f'DON-{donation.id}',
        }
    elif donation.method == 'mobile_money':
        instructions = {
            'ezypesa': 'Dial *150*02# and follow the prompts. Merchant ID: 889900',
            'airtel_money': 'Dial *150*60# and follow the prompts. Business Number: 445566',
            'mpesa': 'Send via M-Pesa. Reference Name: ZANCHANGEMAKERS',
        }
        return {
            'mobile_provider': donation.mobile_provider,
            'instructions': instructions.get(donation.mobile_provider, 'Follow your mobile money provider instructions.'),
            'reference': f'DON-{donation.id}',
        }
    elif donation.method == 'card':
        return {
            'instructions': 'Card payments are not yet processed in demo mode. Please use bank transfer or mobile money.',
        }
    return {}


def confirm_payment(donation, transaction_reference):
    donation.status = 'completed'
    donation.transaction_reference = transaction_reference
    donation.completed_at = timezone.now()
    donation.save()


def fail_payment(donation, reason):
    donation.status = 'failed'
    if donation.message:
        donation.message += f'\nFailure reason: {reason}'
    else:
        donation.message = f'Failure reason: {reason}'
    donation.save()
