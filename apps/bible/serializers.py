from rest_framework import serializers

from .models import (
    BibleBook, BibleChapter, BibleTag, BibleVerse,
    BookHighlight, BookPageNote, BookReadingLog, BookSubtitle,
    FavoriteVerse, HighlightCategory, HighlightTag,
    ReadingProgress, StudyBook, StudyFolder, StudyNote,
    VerseAnnotation, VerseHighlight,
)


class BibleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibleBook
        fields = ['id', 'name', 'abbreviation', 'slug', 'testament',
                  'order', 'total_chapters']


class BibleChapterSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = BibleChapter
        fields = ['id', 'book', 'book_name', 'number', 'total_verses']


class BibleVerseSerializer(serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()

    class Meta:
        model = BibleVerse
        fields = ['id', 'chapter', 'number', 'text', 'reference']

    def get_reference(self, obj):
        return str(obj)


class HighlightCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HighlightCategory
        fields = ['id', 'name', 'color', 'order']
        read_only_fields = ['id']


class BibleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibleTag
        fields = ['id', 'name', 'color']
        read_only_fields = ['id']


class VerseAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerseAnnotation
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VerseHighlightSerializer(serializers.ModelSerializer):
    annotation = VerseAnnotationSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    start_reference = serializers.StringRelatedField(source='start_verse')
    end_reference = serializers.StringRelatedField(source='end_verse')

    class Meta:
        model = VerseHighlight
        fields = [
            'id', 'start_verse', 'end_verse', 'start_reference',
            'end_reference', 'color', 'category', 'annotation',
            'tags', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_tags(self, obj):
        return list(obj.tags.values_list('tag__name', flat=True))


class VerseHighlightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerseHighlight
        fields = ['start_verse', 'end_verse', 'color', 'category']


class FavoriteVerseSerializer(serializers.ModelSerializer):
    verse = BibleVerseSerializer(read_only=True)

    class Meta:
        model = FavoriteVerse
        fields = ['id', 'verse', 'created_at']


class ReadingProgressSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = ReadingProgress
        fields = ['id', 'book', 'book_name', 'chapter', 'last_read_at']


class StudyNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyNote
        fields = ['id', 'category', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ─── Study Folders ─────────────────────────────────────────────────

class StudyFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyFolder
        fields = ['id', 'name', 'color', 'order']
        read_only_fields = ['id']


# ─── Study Books / PDF ─────────────────────────────────────────────

class BookReadingLogSerializer(serializers.ModelSerializer):
    pages_read = serializers.ReadOnlyField()

    class Meta:
        model = BookReadingLog
        fields = ['id', 'page_start', 'page_end', 'notes', 'pages_read', 'date']
        read_only_fields = ['id', 'date']


class BookPageNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookPageNote
        fields = ['id', 'page_number', 'content', 'category', 'folder',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookHighlight
        fields = ['id', 'page_number', 'selected_text', 'rect_data',
                  'annotation', 'title', 'color', 'category', 'folder',
                  'created_at']
        read_only_fields = ['id', 'created_at']


class BookSubtitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSubtitle
        fields = ['id', 'page_number', 'y_position', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudyBookSerializer(serializers.ModelSerializer):
    progress_percent = serializers.ReadOnlyField()

    class Meta:
        model = StudyBook
        fields = [
            'id', 'title', 'author_name', 'category', 'description',
            'cover_image', 'total_pages', 'current_page', 'daily_goal',
            'is_finished', 'progress_percent', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_pages', 'created_at', 'updated_at']


class StudyBookDetailSerializer(serializers.ModelSerializer):
    reading_logs = BookReadingLogSerializer(many=True, read_only=True)
    progress_percent = serializers.ReadOnlyField()

    class Meta:
        model = StudyBook
        fields = [
            'id', 'title', 'author_name', 'category', 'description',
            'cover_image', 'total_pages', 'current_page', 'daily_goal',
            'is_finished', 'progress_percent', 'reading_logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_pages', 'created_at', 'updated_at']
