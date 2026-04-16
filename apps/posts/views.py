from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.filter import check_and_flag
from apps.social.models import Follow, Friendship

from .models import Comment, Post, Reaction, SavedPost
from .serializers import (
    CommentSerializer, PostCreateSerializer, PostSerializer, ReactionSerializer,
)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        friend_ids = set()
        for f in Friendship.objects.filter(Q(user1=user) | Q(user2=user)):
            friend_ids.add(f.user1_id if f.user2_id == user.pk else f.user2_id)
        following_ids = set(
            Follow.objects.filter(follower=user).values_list('followed_id', flat=True),
        )
        visible_users = friend_ids | following_ids | {user.pk}
        return Post.objects.filter(
            Q(author_id__in=visible_users) | Q(is_church_official=True),
        ).select_related('author').prefetch_related('images', 'reactions')


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data.get('content', '')
        title = serializer.validated_data.get('title', '')
        text = f"{title} {content}".strip()
        confirmed = request.data.get('confirmed', False)

        mod_result = check_and_flag(
            user=request.user, text=text,
            content_type='post', content_id=0, confirmed=confirmed,
        )

        if mod_result['severity'] == 'ban':
            return Response({
                'detail': mod_result['warning_message'],
                'severity': 'ban',
            }, status=status.HTTP_403_FORBIDDEN)

        if mod_result['needs_confirmation']:
            return Response({
                'detail': mod_result['warning_message'],
                'needs_confirmation': True,
                'severity': mod_result['severity'],
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer.save(author=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related(
            'images', 'reactions',
        )

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('No puedes editar este post.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('No puedes eliminar este post.')
        instance.delete()


class ReactView(APIView):
    def post(self, request, pk):
        post = generics.get_object_or_404(Post, pk=pk)
        reaction_type = request.data.get('reaction_type', 'like')
        reaction, _ = Reaction.objects.update_or_create(
            user=request.user, post=post,
            defaults={'reaction_type': reaction_type},
        )
        return Response(ReactionSerializer(reaction, context={'request': request}).data)

    def delete(self, request, pk):
        Reaction.objects.filter(user=request.user, post_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['pk'], parent__isnull=True,
        ).select_related('author').prefetch_related('replies__author')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data.get('content', '')
        confirmed = request.data.get('confirmed', False)

        mod_result = check_and_flag(
            user=request.user, text=content,
            content_type='comment', content_id=0, confirmed=confirmed,
        )

        if mod_result['severity'] == 'ban':
            return Response({
                'detail': mod_result['warning_message'],
                'severity': 'ban',
            }, status=status.HTTP_403_FORBIDDEN)

        if mod_result['needs_confirmation']:
            return Response({
                'detail': mod_result['warning_message'],
                'needs_confirmation': True,
                'severity': mod_result['severity'],
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        post_obj = generics.get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(author=request.user, post=post_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SavePostToggleView(APIView):
    def post(self, request, pk):
        post = generics.get_object_or_404(Post, pk=pk)
        saved, created = SavedPost.objects.get_or_create(
            user=request.user, post=post,
        )
        if not created:
            saved.delete()
            return Response({'saved': False})
        return Response({'saved': True})


class SavedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            saved_by__user=self.request.user,
        ).select_related('author').prefetch_related('images', 'reactions')


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            author_id=self.kwargs['user_id'],
        ).select_related('author').prefetch_related('images', 'reactions')
