from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import ProfilePhoto, Story, StoryHighlight, StoryHighlightItem, StoryView


class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = ['id', 'image', 'caption', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class StorySerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    view_count = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'user', 'image', 'text', 'background_color',
                  'created_at', 'expires_at', 'view_count', 'is_viewed']
        read_only_fields = ['id', 'created_at']

    def get_view_count(self, obj):
        if hasattr(obj, '_view_count'):
            return obj._view_count
        return obj.views.count()

    def get_is_viewed(self, obj):
        if hasattr(obj, '_is_viewed'):
            return obj._is_viewed
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.views.filter(viewer=request.user).exists()
        return False


class StoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['image', 'text', 'background_color', 'expires_at']


class StoryHighlightItemSerializer(serializers.ModelSerializer):
    story = StorySerializer(read_only=True)

    class Meta:
        model = StoryHighlightItem
        fields = ['id', 'story', 'order']
        read_only_fields = ['id']


class StoryHighlightSerializer(serializers.ModelSerializer):
    items = StoryHighlightItemSerializer(many=True, read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = StoryHighlight
        fields = ['id', 'name', 'cover_image', 'cover_url', 'order',
                  'created_at', 'items']
        read_only_fields = ['id', 'created_at']

    def get_cover_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        first_item = obj.items.select_related('story').first()
        if first_item and first_item.story.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_item.story.image.url)
            return first_item.story.image.url
        return None


class StoryHighlightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryHighlight
        fields = ['name', 'cover_image', 'order']
