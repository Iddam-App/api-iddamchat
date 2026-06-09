from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services import create_notification

from .models import Follow, FollowRequest, FriendRequest, Friendship
from .serializers import (
    FollowRequestSerializer, FollowSerializer,
    FriendRequestCreateSerializer, FriendRequestSerializer,
    FriendshipSerializer,
)

User = get_user_model()


class SendFriendRequestView(APIView):
    def post(self, request):
        serializer = FriendRequestCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        to_user = User.objects.get(pk=serializer.validated_data['to_user_id'])

        if FriendRequest.objects.filter(
            from_user=request.user, to_user=to_user, status='pending',
        ).exists():
            return Response(
                {'detail': 'Ya enviaste una solicitud.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fr = FriendRequest.objects.create(
            from_user=request.user, to_user=to_user,
            message=serializer.validated_data.get('message', ''),
        )
        create_notification(
            recipient=to_user, sender=request.user,
            notification_type='friend_request',
            message=f'{request.user.display_name} te envió solicitud de amistad.',
            content_type='friend_request', content_id=fr.pk,
        )
        return Response(
            FriendRequestSerializer(fr, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(
            to_user=self.request.user, status='pending',
        ).select_related('from_user', 'to_user')


class SentRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(
            from_user=self.request.user, status='pending',
        ).select_related('from_user', 'to_user')


class RespondFriendRequestView(APIView):
    def post(self, request, pk, action):
        fr = generics.get_object_or_404(
            FriendRequest, pk=pk, to_user=request.user, status='pending',
        )
        if action == 'accept':
            fr.accept()
            create_notification(
                recipient=fr.from_user, sender=request.user,
                notification_type='friend_request_accepted',
                message=f'{request.user.display_name} aceptó tu solicitud de amistad.',
                content_type='friend_request', content_id=fr.pk,
            )
        elif action == 'reject':
            fr.reject()
        else:
            return Response(
                {'detail': 'Acción no válida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(FriendRequestSerializer(fr, context={'request': request}).data)


class FriendListView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            Q(user1=user) | Q(user2=user),
        ).select_related('user1', 'user2')


class FollowToggleView(APIView):
    def post(self, request, user_id):
        target = generics.get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response(
                {'detail': 'No puedes seguirte a ti mismo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already following -> unfollow
        existing_follow = Follow.objects.filter(
            follower=request.user, followed=target,
        ).first()
        if existing_follow:
            existing_follow.delete()
            return Response({'detail': 'Dejaste de seguir.', 'following': False})

        # If target is private, create follow request instead
        if target.is_private:
            # Cancel existing pending request if toggling
            existing_request = FollowRequest.objects.filter(
                from_user=request.user, to_user=target, status='pending',
            ).first()
            if existing_request:
                existing_request.delete()
                return Response({'detail': 'Solicitud cancelada.', 'requested': False})

            fr = FollowRequest.objects.create(
                from_user=request.user, to_user=target,
            )
            create_notification(
                recipient=target, sender=request.user,
                notification_type='follow_request',
                message=f'{request.user.display_name} quiere seguirte.',
                content_type='follow_request', content_id=fr.pk,
            )
            return Response(
                {'detail': 'Solicitud de seguimiento enviada.', 'requested': True},
                status=status.HTTP_201_CREATED,
            )

        # Public account: direct follow
        Follow.objects.create(follower=request.user, followed=target)
        create_notification(
            recipient=target, sender=request.user,
            notification_type='follow',
            message=f'{request.user.display_name} te empezó a seguir.',
        )
        return Response({'detail': 'Ahora sigues a este usuario.', 'following': True})


class FollowersListView(generics.ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(
            followed=self.request.user,
        ).select_related('follower', 'followed')


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user,
        ).select_related('follower', 'followed')


# ─── Follow Request Views ──────────────────────────────────────────

class PendingFollowRequestsView(generics.ListAPIView):
    """Follow requests received by the current user."""
    serializer_class = FollowRequestSerializer

    def get_queryset(self):
        return FollowRequest.objects.filter(
            to_user=self.request.user, status='pending',
        ).select_related('from_user', 'to_user')


class SentFollowRequestsView(generics.ListAPIView):
    """Follow requests sent by the current user."""
    serializer_class = FollowRequestSerializer

    def get_queryset(self):
        return FollowRequest.objects.filter(
            from_user=self.request.user, status='pending',
        ).select_related('from_user', 'to_user')


class RespondFollowRequestView(APIView):
    def post(self, request, pk, action):
        fr = generics.get_object_or_404(
            FollowRequest, pk=pk, to_user=request.user, status='pending',
        )
        if action == 'accept':
            fr.accept()
            create_notification(
                recipient=fr.from_user, sender=request.user,
                notification_type='follow_request_accepted',
                message=f'{request.user.display_name} aceptó tu solicitud de seguimiento.',
                content_type='follow_request', content_id=fr.pk,
            )
        elif action == 'reject':
            fr.reject()
        else:
            return Response(
                {'detail': 'Acción no válida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(FollowRequestSerializer(fr, context={'request': request}).data)
