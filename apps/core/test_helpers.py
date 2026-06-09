from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticatedTestCase(APITestCase):
    """Base test case with an authenticated user."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        )

    def create_user(self, username, email=None, **kwargs):
        """Helper to create additional users."""
        if email is None:
            email = f'{username}@example.com'
        return User.objects.create_user(
            username=username,
            email=email,
            password='TestPass123!',
            first_name=username.capitalize(),
            last_name='User',
            **kwargs,
        )

    def auth_as(self, user):
        """Switch authentication to a different user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        )
