from rest_framework import generics, parsers
from rest_framework.exceptions import ValidationError

from .models import NoteImage, Notebook, NotePage, StudyNote, StudyTopic
from .serializers import (
    NoteImageSerializer, NotePageDetailSerializer, NotePageListSerializer,
    NotebookSerializer, StudyNoteSerializer, StudyTopicSerializer,
)

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


class NotebookListCreateView(generics.ListCreateAPIView):
    serializer_class = NotebookSerializer

    def get_queryset(self):
        return Notebook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotebookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotebookSerializer

    def get_queryset(self):
        return Notebook.objects.filter(user=self.request.user)


class NotePageListCreateView(generics.ListCreateAPIView):
    serializer_class = NotePageListSerializer
    filterset_fields = ['notebook', 'is_favorite']
    search_fields = ['title', 'excerpt']

    def get_queryset(self):
        return NotePage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotePageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotePageDetailSerializer

    def get_queryset(self):
        return NotePage.objects.filter(
            user=self.request.user,
        ).prefetch_related('images', 'subpages')


class NoteImageUploadView(generics.CreateAPIView):
    serializer_class = NoteImageSerializer
    parser_classes = [parsers.MultiPartParser]

    def perform_create(self, serializer):
        image = self.request.FILES.get('image')
        if image:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError('Tipo de imagen no permitido.')
            if image.size > MAX_IMAGE_SIZE:
                raise ValidationError('La imagen excede 10MB.')
        serializer.save(user=self.request.user)


class StudyTopicListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyTopicSerializer

    def get_queryset(self):
        return StudyTopic.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyTopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudyTopicSerializer

    def get_queryset(self):
        return StudyTopic.objects.filter(user=self.request.user)


class StudyNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyNoteSerializer

    def get_queryset(self):
        qs = StudyNote.objects.all()
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            qs = qs.filter(topic_id=topic_id, topic__user=self.request.user)
        return qs


class StudyNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudyNoteSerializer

    def get_queryset(self):
        return StudyNote.objects.filter(topic__user=self.request.user)
