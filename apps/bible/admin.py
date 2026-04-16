from django.contrib import admin

from .models import (
    BibleBook, BibleChapter, BibleVerse,
    HighlightCategory, VerseHighlight, VerseAnnotation,
    BibleTag, FavoriteVerse, ReadingProgress, StudyNote,
)


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'testament', 'order', 'total_chapters')
    list_filter = ('testament',)
    search_fields = ('name', 'abbreviation', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BibleChapter)
class BibleChapterAdmin(admin.ModelAdmin):
    list_display = ('book', 'number', 'total_verses')
    list_filter = ('book__testament', 'book')
    search_fields = ('book__name',)
    raw_id_fields = ('book',)


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'number', 'text_preview')
    list_filter = ('chapter__book__testament', 'chapter__book')
    search_fields = ('text', 'chapter__book__name')
    raw_id_fields = ('chapter',)

    @admin.display(description='Texto')
    def text_preview(self, obj):
        return obj.text[:100]


@admin.register(HighlightCategory)
class HighlightCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'order')
    list_filter = ('color',)
    search_fields = ('name', 'user__username', 'user__email')
    raw_id_fields = ('user',)


@admin.register(VerseHighlight)
class VerseHighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_verse', 'end_verse', 'color', 'category', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('user__username', 'user__email', 'category__name')
    raw_id_fields = ('user', 'start_verse', 'end_verse', 'category')


@admin.register(VerseAnnotation)
class VerseAnnotationAdmin(admin.ModelAdmin):
    list_display = ('user', 'highlight', 'content_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'content')
    raw_id_fields = ('user', 'highlight')

    @admin.display(description='Contenido')
    def content_preview(self, obj):
        return obj.content[:80]


@admin.register(BibleTag)
class BibleTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color')
    list_filter = ('color',)
    search_fields = ('name', 'user__username', 'user__email')
    raw_id_fields = ('user',)


@admin.register(FavoriteVerse)
class FavoriteVerseAdmin(admin.ModelAdmin):
    list_display = ('user', 'verse', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user', 'verse')


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'chapter', 'last_read_at')
    list_filter = ('last_read_at', 'book__testament')
    search_fields = ('user__username', 'user__email', 'book__name')
    raw_id_fields = ('user', 'book', 'chapter')


@admin.register(StudyNote)
class StudyNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username', 'user__email')
    raw_id_fields = ('user', 'category')
