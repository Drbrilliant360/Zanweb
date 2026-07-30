from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from accounts.models import User, VolunteerProfile
from programs.models import Program
from .models import Event, EventRegistration, ImpactLog, Badge, VolunteerBadge, Certificate, CoordinatorMessage


class EventTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123')
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(email='vol@test.com', password='vol12345')
        self.prog = Program.objects.create(name='Test Prog', category='leadership_volunteerism', description='D')
        self.event = Event.objects.create(
            title='Clean-Up', description='Beach clean-up',
            location='Beach', date='2026-08-15', capacity=10,
        )

    def test_list_events(self):
        r = self.client.get('/api/events/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_create_event_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/events/', {
            'title': 'New Event', 'description': 'Desc',
            'location': 'Town', 'date': '2026-09-01',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_event_vol_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/events/', {
            'title': 'New Event', 'description': 'Desc',
            'location': 'Town', 'date': '2026-09-01',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_event(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EventRegistration.objects.filter(event=self.event, volunteer=self.vol).exists())

    def test_register_twice(self):
        self.client.force_authenticate(user=self.vol)
        self.client.post(f'/api/events/{self.event.id}/register/')
        r = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(r.status_code, 200)

    def test_cancel_registration(self):
        self.client.force_authenticate(user=self.vol)
        self.client.post(f'/api/events/{self.event.id}/register/')
        r = self.client.post(f'/api/events/{self.event.id}/cancel_registration/')
        self.assertEqual(r.status_code, 200)
        reg = EventRegistration.objects.get(event=self.event, volunteer=self.vol)
        self.assertEqual(reg.status, 'cancelled')

    def test_cancel_no_registration(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post(f'/api/events/{self.event.id}/cancel_registration/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_registrations(self):
        self.client.force_authenticate(user=self.vol)
        EventRegistration.objects.create(event=self.event, volunteer=self.vol)
        r = self.client.get('/api/my-registrations/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_mark_attended(self):
        reg = EventRegistration.objects.create(event=self.event, volunteer=self.vol)
        # create coordinator for the event to avoid None error in mark_attendance
        coord = User.objects.create_user(email='coord@test.com', password='coord123')
        coord.role = 'coordinator'
        coord.save()
        self.event.coordinator_messages = coord
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/event-registrations/{reg.id}/mark_attended/', {'hours_logged': 5}, format='json')
        self.assertEqual(r.status_code, 200)
        reg.refresh_from_db()
        self.assertEqual(reg.status, 'attended')
        self.assertEqual(reg.hours_logged, 5)

    def test_impact_log_create(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/impact-logs/', {
            'hours': 3, 'date': '2026-07-30', 'description': 'Helped out',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_impact_log_approve(self):
        log = ImpactLog.objects.create(volunteer=self.vol, hours=3, date='2026-07-30')
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/impact-logs/{log.id}/approve/')
        self.assertEqual(r.status_code, 200)
        log.refresh_from_db()
        self.assertTrue(log.is_approved)

    def test_impact_log_volunteer_sees_own(self):
        ImpactLog.objects.create(volunteer=self.vol, hours=3, date='2026-07-30')
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/impact-logs/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_badge_list(self):
        Badge.objects.create(name='First Steps', icon='star')
        r = self.client.get('/api/badges/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_my_badges(self):
        badge = Badge.objects.create(name='First Steps', icon='star')
        VolunteerBadge.objects.create(volunteer=self.vol, badge=badge)
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/my-badges/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_certificate_list_volunteer(self):
        Certificate.objects.create(volunteer=self.vol, title='Completion')
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/certificates/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_certificate_list_admin(self):
        Certificate.objects.create(volunteer=self.vol, title='Completion')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/certificates/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_message_create(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/messages/', {
            'recipient': self.admin.id, 'body': 'Hello admin',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_message_reply(self):
        msg = CoordinatorMessage.objects.create(
            sender=self.admin, recipient=self.vol, body='Welcome',
        )
        self.client.force_authenticate(user=self.vol)
        r = self.client.post(f'/api/messages/{msg.id}/reply/', {'body': 'Thanks!'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_seats_taken_property(self):
        EventRegistration.objects.create(event=self.event, volunteer=self.vol)
        self.assertEqual(self.event.seats_taken, 1)
        self.assertEqual(self.event.seats_remaining, 9)
