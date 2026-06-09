from unittest.mock import patch

from rest_framework import status

from apps.core.test_helpers import AuthenticatedTestCase

from .models import Conversation, Message, MessageTranslation


class ConversationTest(AuthenticatedTestCase):
    def test_start_conversation(self):
        other = self.create_user('other')
        response = self.client.post('/api/chat/conversations/start/', {
            'user_id': other.pk,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('other_user', response.data)

    def test_start_conversation_with_self_rejected(self):
        response = self.client.post('/api/chat/conversations/start/', {
            'user_id': self.user.pk,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_conversations(self):
        other = self.create_user('other')
        u1 = min(self.user, other, key=lambda u: u.pk)
        u2 = max(self.user, other, key=lambda u: u.pk)
        Conversation.objects.create(user1=u1, user2=u2)
        response = self.client.get('/api/chat/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class MessageTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.other = self.create_user('other')
        u1 = min(self.user, self.other, key=lambda u: u.pk)
        u2 = max(self.user, self.other, key=lambda u: u.pk)
        self.conv = Conversation.objects.create(user1=u1, user2=u2)

    def test_send_message(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conv.pk}/send/',
            {'content': 'Hola!'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_send_empty_message_rejected(self):
        response = self.client.post(
            f'/api/chat/conversations/{self.conv.pk}/send/',
            {'content': ''},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_messages(self):
        Message.objects.create(
            conversation=self.conv, sender=self.user, content='Hello',
        )
        response = self.client.get(
            f'/api/chat/conversations/{self.conv.pk}/messages/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_unread_count(self):
        Message.objects.create(
            conversation=self.conv, sender=self.other, content='Hi',
        )
        response = self.client.get('/api/chat/unread/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_read_marks_messages(self):
        Message.objects.create(
            conversation=self.conv, sender=self.other, content='Hi',
        )
        self.client.get(f'/api/chat/conversations/{self.conv.pk}/messages/')
        self.assertEqual(
            Message.objects.filter(is_read=True).count(), 1,
        )


class TranslationTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.other = self.create_user('other')
        u1 = min(self.user, self.other, key=lambda u: u.pk)
        u2 = max(self.user, self.other, key=lambda u: u.pk)
        self.conv = Conversation.objects.create(user1=u1, user2=u2)
        self.msg = Message.objects.create(
            conversation=self.conv, sender=self.other, content='Hello world',
        )

    @patch('apps.chat.translation.translate_text')
    def test_translate_message(self, mock_translate):
        mock_translate.return_value = {
            'translated_text': 'Hola mundo',
            'detected_source_language': 'en',
        }
        response = self.client.post(
            f'/api/chat/messages/{self.msg.pk}/translate/',
            {'target_language': 'es'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['translated_text'], 'Hola mundo')
        self.assertFalse(response.data['cached'])

    @patch('apps.chat.translation.translate_text')
    def test_translate_uses_cache(self, mock_translate):
        MessageTranslation.objects.create(
            message=self.msg, target_language='es',
            translated_text='Hola mundo', source_language='en',
        )
        response = self.client.post(
            f'/api/chat/messages/{self.msg.pk}/translate/',
            {'target_language': 'es'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['cached'])
        mock_translate.assert_not_called()

    def test_translate_unauthorized(self):
        third = self.create_user('third')
        self.auth_as(third)
        response = self.client.post(
            f'/api/chat/messages/{self.msg.pk}/translate/',
            {'target_language': 'es'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
