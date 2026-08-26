from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, VolunteerProfile
from programs.models import Program
from volunteering.models import Event, EventRegistration


class DashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123')
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(email='vol@test.com', password='vol12345')
        vp, _ = VolunteerProfile.objects.get_or_create(user=self.vol)
        vp.location = 'Zanzibar'
        vp.save()

    def test_volunteer_dashboard_auth_required(self):
        r = self.client.get('/api/dashboard/volunteer/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_volunteer_dashboard_structure(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/dashboard/volunteer/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('greeting_name', r.data)
        self.assertIn('total_impact_hours', r.data)
        self.assertIn('rank', r.data)
        self.assertIn('next_rank_threshold_hours', r.data)
        self.assertIn('percent_to_next_rank', r.data)
        self.assertIn('upcoming_shifts', r.data)
        self.assertIn('recognitions', r.data)
        self.assertIn('latest_coordinator_message', r.data)
        self.assertEqual(r.data['percent_to_next_rank'], 0)
        self.assertEqual(r.data['total_impact_hours'], 0)
        self.assertEqual(r.data['rank'], 'newcomer')

    def test_volunteer_dashboard_with_event(self):
        event = Event.objects.create(
            title='Clean-Up', description='Desc',
            location='Beach', date='2026-08-15',
        )
        EventRegistration.objects.create(event=event, volunteer=self.vol)
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/dashboard/volunteer/')
        self.assertEqual(len(r.data['upcoming_shifts']), 1)
        self.assertEqual(r.data['upcoming_shifts'][0]['event_title'], 'Clean-Up')

    def test_volunteer_dashboard_rank_matches_profile(self):
        vp, _ = VolunteerProfile.objects.get_or_create(user=self.vol)
        vp.total_impact_hours = 50
        vp.save(update_fields=['total_impact_hours'])
        vp.recompute_rank()
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/dashboard/volunteer/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['rank'], vp.rank)
        self.assertEqual(r.data['next_rank_threshold_hours'], float(vp.next_rank_threshold_hours))
        self.assertEqual(r.data['percent_to_next_rank'], 16)

    def test_admin_dashboard_auth_required(self):
        r = self.client.get('/api/dashboard/admin/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_dashboard_vol_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/dashboard/admin/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_dashboard_structure(self):
        Program.objects.create(
            name='Test Program', category='leadership_volunteerism',
            description='Desc', status='active', is_published=True,
        )
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/dashboard/admin/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('as_of', r.data)
        self.assertIn('total_volunteers', r.data)
        self.assertIn('active_programs', r.data)
        self.assertIn('grants_awarded', r.data)
        self.assertIn('recent_applications', r.data)
        self.assertIn('program_tracking', r.data)
        self.assertIn('engagement_by_category', r.data)
        self.assertEqual(r.data['total_volunteers'], 1)
        self.assertEqual(r.data['active_programs'], 1)
