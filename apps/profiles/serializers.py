from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import ProfilePhoto, Story, StoryView


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
