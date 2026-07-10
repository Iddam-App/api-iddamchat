from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProfilePhoto, Story, StoryHighlight, StoryHighlightItem, StoryView
from .serializers import (
    ProfilePhotoSerializer, StoryCreateSerializer,
    StoryHighlightCreateSerializer, StoryHighlightSerializer, StorySerializer,
)


class ProfilePhotoListCreateView(generics.ListCreateAPIView):
    serializer_class = ProfilePhotoSerializer

    def get_queryset(self):
        return ProfilePhoto.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfilePhotoDeleteView(generics.DestroyAPIView):
    serializer_class = ProfilePhotoSerializer

    def get_queryset(self):
        return ProfilePhoto.objects.filter(user=self.request.user)


class StoryFeedView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        from django.db.models import Q
        from apps.social.models import Follow
        user = self.request.user

        following_ids = Follow.objects.filter(
            follower=user,
        ).values_list('followed_id', flat=True)

        return Story.objects.filter(
            expires_at__gt=timezone.now(),
        ).filter(
            # My stories, or public accounts, or private accounts I follow
            Q(user=user) |
            Q(user__is_private=False) |
            Q(user_id__in=following_ids),
        ).select_related('user').annotate(
            _view_count=Count('views', distinct=True),
            _is_viewed=Exists(
                StoryView.objects.filter(story=OuterRef('pk'), viewer=user),
            ),
        ).order_by('-created_at')


class StoryCreateView(generics.CreateAPIView):
    serializer_class = StoryCreateSerializer

    def perform_create(self, serializer):
        if not serializer.validated_data.get('expires_at'):
            serializer.validated_data['expires_at'] = (
                timezone.now() + timezone.timedelta(hours=24)
            )
        serializer.save(user=self.request.user)


class StoryViewRegister(APIView):
    def post(self, request, pk):
        story = generics.get_object_or_404(Story, pk=pk)
        StoryView.objects.get_or_create(story=story, viewer=request.user)
        return Response({'detail': 'Vista registrada.'})


class MyStoriesView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user).order_by('-created_at')


class UserStoriesView(generics.ListAPIView):
    """All stories for a user (including expired), used for highlight picker."""
    serializer_class = StorySerializer

    def get_queryset(self):
        return Story.objects.filter(
            user_id=self.kwargs['user_id'],
        ).order_by('-created_at')


class StoryHighlightListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StoryHighlightCreateSerializer
        return StoryHighlightSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return StoryHighlight.objects.filter(
                user_id=user_id,
            ).prefetch_related('items__story')
        return StoryHighlight.objects.filter(
            user=self.request.user,
        ).prefetch_related('items__story')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StoryHighlightDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoryHighlightSerializer

    def get_queryset(self):
        return StoryHighlight.objects.filter(
            user=self.request.user,
        ).prefetch_related('items__story')


class StoryHighlightAddItemView(APIView):
    def post(self, request, pk):
        highlight = generics.get_object_or_404(
            StoryHighlight, pk=pk, user=request.user,
        )
        story_id = request.data.get('story_id')
        story = generics.get_object_or_404(Story, pk=story_id, user=request.user)
        item, created = StoryHighlightItem.objects.get_or_create(
            highlight=highlight, story=story,
            defaults={'order': highlight.items.count()},
        )
        if not created:
            return Response(
                {'detail': 'Ya está en este destacado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Agregada.'}, status=status.HTTP_201_CREATED)


class StoryHighlightRemoveItemView(APIView):
    def delete(self, request, pk, item_id):
        highlight = generics.get_object_or_404(
            StoryHighlight, pk=pk, user=request.user,
        )
        StoryHighlightItem.objects.filter(
            pk=item_id, highlight=highlight,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
