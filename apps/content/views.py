from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, ChurchService, Podcast, SavedContent
from .serializers import (
    ArticleSerializer, ChurchServiceSerializer, PodcastSerializer,
    SavedContentSerializer,
)


class PodcastListView(generics.ListAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    filterset_fields = ['series']
    search_fields = ['title', 'description']


class PodcastDetailView(generics.RetrieveAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer


class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title', 'content', 'excerpt']


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'


class ChurchServiceListView(generics.ListAPIView):
    queryset = ChurchService.objects.all()
    serializer_class = ChurchServiceSerializer
    filterset_fields = ['service_type']
    search_fields = ['title', 'speaker']


class ChurchServiceDetailView(generics.RetrieveAPIView):
    queryset = ChurchService.objects.all()
    serializer_class = ChurchServiceSerializer


class SaveContentView(APIView):
    def post(self, request):
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')

        kwargs = {'user': request.user, 'content_type': content_type}
        if content_type == 'podcast':
            kwargs['podcast_id'] = content_id
        elif content_type == 'article':
            kwargs['article_id'] = content_id
        elif content_type == 'service':
            kwargs['service_id'] = content_id
        else:
            return Response(
                {'detail': 'Tipo no válido.'}, status=status.HTTP_400_BAD_REQUEST,
            )

        saved, created = SavedContent.objects.get_or_create(**kwargs)
        if not created:
            saved.delete()
            return Response({'saved': False})
        return Response({'saved': True})


class SavedContentListView(generics.ListAPIView):
    serializer_class = SavedContentSerializer

    def get_queryset(self):
        return SavedContent.objects.filter(
            user=self.request.user,
        ).select_related('podcast', 'article', 'service')
