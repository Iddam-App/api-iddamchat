from django.contrib import admin

from .models import Podcast, Article, ChurchService, SavedContent


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'series', 'episode_number', 'duration_minutes',
        'published_at', 'created_at',
    )
    list_filter = ('series', 'published_at', 'created_at')
    search_fields = ('title', 'description', 'series')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author_name', 'category', 'is_featured',
        'published_at', 'created_at',
    )
    list_filter = ('category', 'is_featured', 'published_at', 'created_at')
    search_fields = ('title', 'author_name', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ChurchService)
class ChurchServiceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'service_type', 'speaker', 'date',
        'duration_minutes', 'created_at',
    )
    list_filter = ('service_type', 'date', 'created_at')
    search_fields = ('title', 'description', 'speaker')


@admin.register(SavedContent)
class SavedContentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'podcast', 'article', 'service', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user', 'podcast', 'article', 'service')
