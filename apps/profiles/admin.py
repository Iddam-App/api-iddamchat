from django.contrib import admin

from .models import ProfilePhoto, Story, StoryView


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('user__username', 'user__email', 'caption')
    raw_id_fields = ('user',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'background_color', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'text')
    raw_id_fields = ('user',)


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'viewer', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('story__user__username', 'viewer__username')
    raw_id_fields = ('story', 'viewer')
