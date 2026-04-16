from rest_framework import serializers

from .models import NoteImage, Notebook, NotePage, StudyNote, StudyTopic


class NotebookSerializer(serializers.ModelSerializer):
    page_count = serializers.ReadOnlyField()

    class Meta:
        model = Notebook
        fields = ['id', 'parent', 'title', 'icon', 'color', 'order',
                  'page_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoteImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteImage
        fields = ['id', 'image', 'caption', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotePageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotePage
        fields = ['id', 'notebook', 'parent', 'title', 'icon',
                  'cover_image', 'excerpt', 'is_favorite', 'order',
                  'created_at', 'updated_at']


class NotePageDetailSerializer(serializers.ModelSerializer):
    images = NoteImageSerializer(many=True, read_only=True)
    subpages = NotePageListSerializer(many=True, read_only=True)

    class Meta:
        model = NotePage
        fields = [
            'id', 'notebook', 'parent', 'title', 'icon', 'cover_image',
            'content', 'excerpt', 'is_favorite', 'order', 'images',
            'subpages', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudyTopicSerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = ['id', 'title', 'description', 'icon', 'color',
                  'cover_image', 'order', 'note_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_note_count(self, obj):
        return obj.notes.count()


class StudyNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyNote
        fields = ['id', 'topic', 'title', 'content', 'order',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
