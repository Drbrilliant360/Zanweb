from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import ContactMessage, NewsletterSubscriber, Partner, Story, GalleryImage, FAQ, OrgStat


class EngagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123')
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(email='vol@test.com', password='vol12345')
        self.faq = FAQ.objects.create(
            topic='Donations', keywords='donate, give, contribute',
            question_example='How to donate?',
            answer='You can donate via mobile money.',
            sort_order=1, is_active=True,
        )

    def test_contact_message_create(self):
        r = self.client.post('/api/contact-messages/', {
            'name': 'Test User', 'email': 'test@test.com',
            'subject': 'Question', 'message': 'Hello',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_contact_message_list_admin(self):
        ContactMessage.objects.create(name='T', email='t@t.com', subject='S', message='M')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/contact-messages/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_contact_message_list_non_admin(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/contact-messages/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_read(self):
        msg = ContactMessage.objects.create(name='T', email='t@t.com', subject='S', message='M')
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/contact-messages/{msg.id}/mark_read/')
        self.assertEqual(r.status_code, 200)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_newsletter_subscribe(self):
        r = self.client.post('/api/newsletter/', {'email': 'sub@test.com'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='sub@test.com').exists())

    def test_newsletter_duplicate(self):
        NewsletterSubscriber.objects.create(email='sub@test.com')
        r = self.client.post('/api/newsletter/', {'email': 'sub@test.com'}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_newsletter_reactivate(self):
        NewsletterSubscriber.objects.create(email='sub@test.com', is_active=False)
        r = self.client.post('/api/newsletter/', {'email': 'sub@test.com'}, format='json')
        self.assertEqual(r.status_code, 200)
        sub = NewsletterSubscriber.objects.get(email='sub@test.com')
        self.assertTrue(sub.is_active)

    def test_newsletter_no_email(self):
        r = self.client.post('/api/newsletter/', {}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partner_create_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/partners/', {
            'name': 'Test Partner', 'type': 'corporate',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_partner_create_vol_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/partners/', {'name': 'Test', 'type': 'corporate'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_story_create_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/stories/', {
            'title': 'Test Story', 'author': 'Author',
            'excerpt': 'Exc', 'content': 'Full content',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_gallery_list(self):
        GalleryImage.objects.create(caption='Test Image', category='yvf')
        r = self.client.get('/api/gallery/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_faq_list(self):
        r = self.client.get('/api/faq/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data), 1)

    def test_faq_match_exact(self):
        r = self.client.get('/api/faq/match/?q=how+to+donate')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['topic'], 'Donations')

    def test_faq_match_partial(self):
        r = self.client.get('/api/faq/match/?q=give+money')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['topic'], 'Donations')

    def test_faq_match_no_match(self):
        r = self.client.get('/api/faq/match/?q=xyzzy+nonexistent')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['topic'], 'No specific match')

    def test_faq_match_no_query(self):
        r = self.client.get('/api/faq/match/')
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data['answer'])

    def test_org_stat_list(self):
        OrgStat.objects.create(label='Volunteers', value='100+', icon='users', order=1)
        r = self.client.get('/api/org-stats/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)
