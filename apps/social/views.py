from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, FriendRequest, Friendship
from .serializers import (
    FollowSerializer, FriendRequestCreateSerializer,
    FriendRequestSerializer, FriendshipSerializer,
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
        follow, created = Follow.objects.get_or_create(
            follower=request.user, followed=target,
        )
        if not created:
            follow.delete()
            return Response({'detail': 'Dejaste de seguir.', 'following': False})
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
