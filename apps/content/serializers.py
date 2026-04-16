from rest_framework import serializers

from .models import Article, ChurchService, Podcast, SavedContent


class PodcastSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Podcast
        fields = [
            'id', 'title', 'description', 'audio_url', 'cover_image',
            'duration_minutes', 'episode_number', 'series',
            'external_url', 'published_at', 'is_saved',
        ]

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedContent.objects.filter(
                user=request.user, podcast=obj,
            ).exists()
        return False


class ArticleSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author_name', 'category',
            'content', 'excerpt', 'cover_image', 'external_url',
            'is_featured', 'published_at', 'is_saved',
        ]

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedContent.objects.filter(
                user=request.user, article=obj,
            ).exists()
        return False


class ChurchServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchService
        fields = [
            'id', 'title', 'service_type', 'description', 'video_url',
            'audio_url', 'speaker', 'date', 'duration_minutes',
        ]


class SavedContentSerializer(serializers.ModelSerializer):
    podcast = PodcastSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)
    service = ChurchServiceSerializer(read_only=True)

    class Meta:
        model = SavedContent
        fields = ['id', 'content_type', 'podcast', 'article', 'service', 'created_at']
