from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Program, Cohort, ProgramApplication
from accounts.models import User


class ProgramTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123')
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(email='vol@test.com', password='vol12345')
        self.p1 = Program.objects.create(
            name='Leadership Program', category='leadership_volunteerism',
            description='Desc', short_description='Short',
            status='active', is_published=True,
        )
        self.p2 = Program.objects.create(
            name='Draft Program', category='digital_skills',
            description='Desc', is_published=False,
        )
        self.cohort = Cohort.objects.create(program=self.p1, number=1, name='Cohort 1')
        self.app = ProgramApplication.objects.create(
            program=self.p1, full_name='Test App', email='app@test.com',
            status='pending',
        )

    def test_list_published_programs(self):
        r = self.client.get('/api/programs/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_list_all_programs_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/programs/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 2)

    def test_retrieve_program(self):
        r = self.client.get(f'/api/programs/{self.p1.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Leadership Program')

    def test_create_program_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/programs/', {
            'name': 'New Program', 'category': 'health_wellbeing',
            'description': 'Desc', 'status': 'planning',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_program_as_volunteer_forbidden(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/programs/', {
            'name': 'New Program', 'category': 'health_wellbeing',
            'description': 'Desc',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_program_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.patch(f'/api/programs/{self.p1.id}/', {'name': 'Updated'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Updated')

    def test_delete_program_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/programs/{self.p2.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_cohorts(self):
        r = self.client.get('/api/cohorts/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_list_applications(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/applications/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_create_application(self):
        r = self.client.post('/api/applications/', {
            'full_name': 'New App', 'email': 'new@test.com',
            'program': self.p1.id, 'message': 'I want to join',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_review_application(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/applications/{self.app.id}/review/', {
            'decision': 'approved', 'review_notes': 'Great fit',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, 'approved')
