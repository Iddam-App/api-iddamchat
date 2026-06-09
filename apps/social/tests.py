from rest_framework import status

from apps.core.test_helpers import AuthenticatedTestCase
from apps.social.models import Follow, FollowRequest, Friendship


class FollowTest(AuthenticatedTestCase):
    def test_follow_public_user(self):
        other = self.create_user('other')
        response = self.client.post(f'/api/social/follow/{other.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['following'])
        self.assertTrue(Follow.objects.filter(
            follower=self.user, followed=other,
        ).exists())

    def test_unfollow(self):
        other = self.create_user('other')
        Follow.objects.create(follower=self.user, followed=other)
        response = self.client.post(f'/api/social/follow/{other.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['following'])

    def test_follow_self_rejected(self):
        response = self.client.post(f'/api/social/follow/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_followers_list(self):
        other = self.create_user('follower')
        Follow.objects.create(follower=other, followed=self.user)
        response = self.client.get('/api/social/followers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_following_list(self):
        other = self.create_user('followed')
        Follow.objects.create(follower=self.user, followed=other)
        response = self.client.get('/api/social/following/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class PrivateAccountFollowTest(AuthenticatedTestCase):
    def test_follow_private_creates_request(self):
        private_user = self.create_user('private', is_private=True)
        response = self.client.post(f'/api/social/follow/{private_user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['requested'])
        self.assertFalse(Follow.objects.filter(
            follower=self.user, followed=private_user,
        ).exists())
        self.assertTrue(FollowRequest.objects.filter(
            from_user=self.user, to_user=private_user, status='pending',
        ).exists())

    def test_cancel_follow_request(self):
        private_user = self.create_user('private', is_private=True)
        FollowRequest.objects.create(
            from_user=self.user, to_user=private_user,
        )
        response = self.client.post(f'/api/social/follow/{private_user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['requested'])

    def test_accept_follow_request(self):
        requester = self.create_user('requester')
        private_user = self.create_user('private', is_private=True)
        fr = FollowRequest.objects.create(
            from_user=requester, to_user=private_user,
        )
        self.auth_as(private_user)
        response = self.client.post(f'/api/social/follow-requests/{fr.pk}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Follow.objects.filter(
            follower=requester, followed=private_user,
        ).exists())

    def test_reject_follow_request(self):
        requester = self.create_user('requester')
        private_user = self.create_user('private', is_private=True)
        fr = FollowRequest.objects.create(
            from_user=requester, to_user=private_user,
        )
        self.auth_as(private_user)
        response = self.client.post(f'/api/social/follow-requests/{fr.pk}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Follow.objects.filter(
            follower=requester, followed=private_user,
        ).exists())

    def test_pending_follow_requests(self):
        requester = self.create_user('requester')
        self.user.is_private = True
        self.user.save()
        FollowRequest.objects.create(
            from_user=requester, to_user=self.user,
        )
        response = self.client.get('/api/social/follow-requests/pending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_sent_follow_requests(self):
        private_user = self.create_user('private', is_private=True)
        FollowRequest.objects.create(
            from_user=self.user, to_user=private_user,
        )
        response = self.client.get('/api/social/follow-requests/sent/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class FriendRequestTest(AuthenticatedTestCase):
    def test_send_friend_request(self):
        other = self.create_user('other')
        response = self.client.post('/api/social/friends/request/', {
            'to_user_id': other.pk,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accept_friend_request(self):
        other = self.create_user('other')
        from apps.social.models import FriendRequest
        fr = FriendRequest.objects.create(
            from_user=other, to_user=self.user,
        )
        response = self.client.post(f'/api/social/friends/request/{fr.pk}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Friendship.objects.filter(
            user1=min(self.user, other, key=lambda u: u.pk),
            user2=max(self.user, other, key=lambda u: u.pk),
        ).exists())

    def test_friend_list(self):
        other = self.create_user('friend')
        u1 = min(self.user, other, key=lambda u: u.pk)
        u2 = max(self.user, other, key=lambda u: u.pk)
        Friendship.objects.create(user1=u1, user2=u2)
        response = self.client.get('/api/social/friends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
