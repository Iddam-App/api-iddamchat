from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProfilePhoto, Story, StoryView
from .serializers import (
    ProfilePhotoSerializer, StoryCreateSerializer, StorySerializer,
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
