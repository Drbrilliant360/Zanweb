from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User, VolunteerProfile


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='admin123',
            first_name='Admin', last_name='User',
        )
        self.admin.role = 'admin'
        self.admin.save()
        self.vol = User.objects.create_user(
            email='vol@test.com', password='vol12345',
            first_name='Vol', last_name='User',
        )
        self.vol.role = 'volunteer'
        self.vol.save()
        vp, _ = VolunteerProfile.objects.get_or_create(user=self.vol)
        vp.location = 'Zanzibar'
        vp.save()

    def test_register_success(self):
        data = {
            'email': 'new@test.com', 'password': 'testpass123', 'password2': 'testpass123',
            'first_name': 'New', 'last_name': 'User',
            'accepted_terms': True, 'accepted_privacy_policy': True,
        }
        r = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', r.data)
        self.assertIn('user', r.data)
        self.assertEqual(r.data['user']['email'], 'new@test.com')

    def test_register_duplicate_email(self):
        data = {
            'email': 'vol@test.com', 'password': 'testpass123', 'password2': 'testpass123',
            'accepted_terms': True, 'accepted_privacy_policy': True,
        }
        r = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {
            'email': 'new2@test.com', 'password': 'testpass123', 'password2': 'wrongpass',
            'accepted_terms': True, 'accepted_privacy_policy': True,
        }
        r = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        r = self.client.post('/api/auth/login/', {'email': 'vol@test.com', 'password': 'vol12345'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_login_invalid(self):
        r = self.client.post('/api/auth/login/', {'email': 'vol@test.com', 'password': 'wrong'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        r = self.client.post('/api/auth/login/', {'email': 'vol@test.com', 'password': 'vol12345'}, format='json')
        refresh = r.data['refresh']
        r2 = self.client.post('/api/auth/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('access', r2.data)

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], 'vol@test.com')

    def test_me_unauthenticated(self):
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_update(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.patch('/api/auth/me/', {'first_name': 'Updated', 'phone_number': '+255777000111'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['first_name'], 'Updated')

    def test_logout(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/auth/logout/', {'refresh': ''}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_change_password(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/auth/change-password/', {'current_password': 'vol12345', 'new_password': 'newpass1234'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.vol.refresh_from_db()
        self.assertTrue(self.vol.check_password('newpass1234'))

    def test_change_password_wrong_current(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.post('/api/auth/change-password/', {'current_password': 'wrong', 'new_password': 'newpass1234'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_volunteer_list(self):
        u = User.objects.create_user(email='another@test.com', password='pass12345', first_name='Another')
        vp, _ = VolunteerProfile.objects.get_or_create(user=u)
        vp.location = 'Dar es Salaam'
        vp.is_active_volunteer = True
        vp.save()
        r = self.client.get('/api/volunteers/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data['results']), 2)

    def test_volunteer_list_search(self):
        r = self.client.get('/api/volunteers/?search=Zanzibar')
        self.assertEqual(r.status_code, 200)

    def test_volunteer_detail_admin(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get(f'/api/volunteers/{self.vol.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], 'vol@test.com')

    def test_volunteer_detail_non_admin(self):
        self.client.force_authenticate(user=self.vol)
        r = self.client.get(f'/api/volunteers/{self.vol.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
