from rest_framework import status

from apps.core.test_helpers import AuthenticatedTestCase
from apps.notifications.models import Notification
from apps.notifications.services import create_notification


class NotificationServiceTest(AuthenticatedTestCase):
    def test_create_notification(self):
        other = self.create_user('other')
        notif = create_notification(
            recipient=self.user, sender=other,
            notification_type='follow',
            message='Other te empezó a seguir.',
        )
        self.assertIsNotNone(notif)
        self.assertEqual(Notification.objects.count(), 1)

    def test_skip_self_notification(self):
        notif = create_notification(
            recipient=self.user, sender=self.user,
            notification_type='follow',
            message='Self follow.',
        )
        self.assertIsNone(notif)
        self.assertEqual(Notification.objects.count(), 0)


class NotificationViewTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.other = self.create_user('sender')
        for i in range(3):
            Notification.objects.create(
                recipient=self.user, sender=self.other,
                notification_type='like',
                message=f'Notification {i}',
            )

    def test_list_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_unread_count(self):
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 3)

    def test_mark_read(self):
        notif = Notification.objects.filter(recipient=self.user).first()
        response = self.client.post(f'/api/notifications/{notif.pk}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_read(self):
        response = self.client.post('/api/notifications/read-all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=False).count(),
            0,
        )

    def test_follow_creates_notification(self):
        """Integration: following someone creates a notification."""
        Notification.objects.all().delete()
        target = self.create_user('target')
        self.client.post(f'/api/social/follow/{target.pk}/')
        self.assertEqual(
            Notification.objects.filter(
                recipient=target, notification_type='follow',
            ).count(),
            1,
        )
