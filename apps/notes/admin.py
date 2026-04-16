from django.contrib import admin

from .models import Notebook, NotePage, NoteImage, StudyTopic, StudyNote


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'parent', 'color', 'order', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email')
    raw_id_fields = ('user', 'parent')


@admin.register(NotePage)
class NotePageAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'notebook', 'is_favorite',
        'order', 'created_at', 'updated_at',
    )
    list_filter = ('is_favorite', 'created_at', 'updated_at')
    search_fields = ('title', 'excerpt', 'user__username', 'user__email')
    raw_id_fields = ('user', 'notebook', 'parent')


@admin.register(NoteImage)
class NoteImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'page', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('caption', 'user__username', 'user__email')
    raw_id_fields = ('user', 'page')


@admin.register(StudyTopic)
class StudyTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'color', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'user__username', 'user__email')
    raw_id_fields = ('user',)


@admin.register(StudyNote)
class StudyNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content', 'topic__title')
    raw_id_fields = ('topic',)
