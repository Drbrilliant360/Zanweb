from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import DonationCampaign, DonationTier, Donation


class DonationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123')
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(email='vol@test.com', password='vol12345')
        self.camp = DonationCampaign.objects.create(
            title='School Drive', description='Help schools',
            goal_amount=50000, is_active=True,
        )
        self.tier = DonationTier.objects.create(
            campaign=self.camp, name='Supporter', amount=10.00,
        )

    def test_list_active_campaigns(self):
        DonationCampaign.objects.create(title='Inactive', description='N', goal_amount=100, is_active=False)
        r = self.client.get('/api/donation-campaigns/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_create_campaign_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/donation-campaigns/', {
            'title': 'New Campaign', 'description': 'Desc', 'goal_amount': 1000,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_campaign_vol_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/donation-campaigns/', {
            'title': 'New Campaign', 'description': 'Desc', 'goal_amount': 1000,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_donation(self):
        r = self.client.post('/api/donations/', {
            'campaign': self.camp.id, 'amount': 25.00,
            'method': 'mobile_money', 'mobile_provider': 'mpesa',
            'donor_name': 'Test Donor', 'donor_email': 'donor@test.com',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_instructions', r.data)
        self.assertIn('donation', r.data)

    def test_create_donation_with_anonymous(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/donations/', {
            'campaign': self.camp.id, 'amount': 50.00,
            'method': 'mobile_money', 'mobile_provider': 'ezypesa',
            'is_anonymous': True, 'message': 'Keep it up!',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_instructions', r.data)

    def test_list_donations_admin(self):
        Donation.objects.create(
            campaign=self.camp, amount=25, method='mobile_money',
            donor_name='T', donor_email='t@t.com',
        )
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/donations/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_list_donations_vol_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/donations/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_confirm_donation(self):
        d = Donation.objects.create(
            campaign=self.camp, amount=25, method='bank_transfer',
            donor_name='T', donor_email='t@t.com',
        )
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/donations/{d.id}/confirm/', {
            'transaction_reference': 'TXN-12345',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        d.refresh_from_db()
        self.assertEqual(d.status, 'completed')
        self.assertEqual(d.transaction_reference, 'TXN-12345')

    def test_mark_failed(self):
        d = Donation.objects.create(
            campaign=self.camp, amount=25, method='card',
            donor_name='T', donor_email='t@t.com',
        )
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/donations/{d.id}/mark_failed/', {'reason': 'Card declined'}, format='json')
        self.assertEqual(r.status_code, 200)
        d.refresh_from_db()
        self.assertEqual(d.status, 'failed')

    def test_percent_achieved(self):
        self.assertEqual(self.camp.percent_achieved, 0)
        self.camp.raised_amount = 25000
        self.camp.save()
        self.assertEqual(self.camp.percent_achieved, 50.0)
