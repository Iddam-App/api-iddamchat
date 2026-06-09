from django.db.models import Count, Exists, OuterRef, Q, Subquery
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.filter import check_and_flag
from apps.notifications.services import create_notification
from apps.social.models import Follow, Friendship

from .models import Comment, Post, Reaction, SavedPost
from .serializers import (
    CommentSerializer, PostCreateSerializer, PostSerializer, ReactionSerializer,
)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        friend_ids = set(
            Friendship.objects.filter(
                Q(user1=user) | Q(user2=user),
            ).values_list('user1_id', 'user2_id').distinct()
        )
        # Flatten and remove self
        flat_friend_ids = set()
        for u1, u2 in friend_ids:
            flat_friend_ids.add(u1 if u2 == user.pk else u2)

        following_ids = set(
            Follow.objects.filter(follower=user).values_list('followed_id', flat=True),
        )
        visible_users = flat_friend_ids | following_ids | {user.pk}

        return Post.objects.filter(
            Q(author_id__in=visible_users) | Q(is_church_official=True),
        ).select_related('author').prefetch_related(
            'images', 'reactions',
        ).annotate(
            _reaction_count=Count('reactions', distinct=True),
            _comment_count=Count('comments', distinct=True),
            _is_saved=Exists(
                SavedPost.objects.filter(user=user, post=OuterRef('pk')),
            ),
        )


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
        reaction, created = Reaction.objects.update_or_create(
            user=request.user, post=post,
            defaults={'reaction_type': reaction_type},
        )
        if created:
            create_notification(
                recipient=post.author, sender=request.user,
                notification_type='like',
                message=f'{request.user.display_name} reaccionó a tu publicación.',
                content_type='post', content_id=post.pk,
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
        comment = serializer.save(author=request.user, post=post_obj)
        create_notification(
            recipient=post_obj.author, sender=request.user,
            notification_type='comment',
            message=f'{request.user.display_name} comentó en tu publicación.',
            content_type='post', content_id=post_obj.pk,
        )
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
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user_id = self.kwargs['user_id']
        try:
            target = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Post.objects.none()

        # Privacy guard: private account + not following = no posts
        if target.is_private and target != self.request.user:
            if not Follow.objects.filter(
                follower=self.request.user, followed=target,
            ).exists():
                return Post.objects.none()

        qs = Post.objects.filter(
            author_id=user_id,
        ).select_related('author').prefetch_related('images', 'reactions')
        # If viewing someone else's profile, hide hidden posts
        if self.request.user.pk != user_id:
            qs = qs.filter(is_hidden=False)
        return qs


class HobbiesFeedView(generics.ListAPIView):
    """Public feed of all hobby-type posts."""
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            post_type='hobby', is_hidden=False,
        ).select_related('author').prefetch_related('images', 'reactions').order_by('-created_at')


class ToggleHidePostView(APIView):
    def post(self, request, pk):
        post = generics.get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            raise PermissionDenied('No puedes modificar este post.')
        post.is_hidden = not post.is_hidden
        post.save(update_fields=['is_hidden'])
        return Response({'is_hidden': post.is_hidden})
