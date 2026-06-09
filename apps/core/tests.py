from rest_framework import status

from .test_helpers import AuthenticatedTestCase


class RegisterTest(AuthenticatedTestCase):
    def test_register_success(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_register_password_mismatch(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password_confirm': 'WrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTest(AuthenticatedTestCase):
    def test_get_me(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_me(self):
        response = self.client.patch('/api/auth/me/', {
            'nickname': 'TestNick',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'TestNick')

    def test_update_privacy(self):
        response = self.client.patch('/api/auth/me/', {
            'is_private': True,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_private'])


class UserProfileTest(AuthenticatedTestCase):
    def test_view_public_profile(self):
        other = self.create_user('other')
        response = self.client.get(f'/api/auth/users/{other.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('is_restricted', response.data)

    def test_view_private_profile_restricted(self):
        other = self.create_user('private_user', is_private=True)
        response = self.client.get(f'/api/auth/users/{other.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('is_restricted'))


class ChangePasswordTest(AuthenticatedTestCase):
    def test_change_password(self):
        response = self.client.post('/api/auth/me/password/', {
            'old_password': 'TestPass123!',
            'new_password': 'NewStrongPass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old(self):
        response = self.client.post('/api/auth/me/password/', {
            'old_password': 'WrongPassword',
            'new_password': 'NewStrongPass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLanguageTest(AuthenticatedTestCase):
    def test_add_language(self):
        response = self.client.post('/api/auth/me/languages/', {
            'language_code': 'en',
            'language_name': 'English',
            'is_native': False,
            'proficiency': 'fluent',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_languages(self):
        self.client.post('/api/auth/me/languages/', {
            'language_code': 'es',
            'language_name': 'Español',
            'is_native': True,
            'proficiency': 'native',
        })
        response = self.client.get('/api/auth/me/languages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_language(self):
        resp = self.client.post('/api/auth/me/languages/', {
            'language_code': 'fr',
            'language_name': 'Français',
        })
        lang_id = resp.data['id']
        response = self.client.delete(f'/api/auth/me/languages/{lang_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_available_languages(self):
        response = self.client.get('/api/auth/languages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 10)
