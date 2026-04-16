from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BibleBook, BibleChapter, BibleTag, BibleVerse,
    FavoriteVerse, HighlightCategory, HighlightTag,
    ReadingProgress, StudyNote, VerseAnnotation, VerseHighlight,
)
from .serializers import (
    BibleBookSerializer, BibleChapterSerializer, BibleTagSerializer,
    BibleVerseSerializer, FavoriteVerseSerializer,
    HighlightCategorySerializer, ReadingProgressSerializer,
    StudyNoteSerializer, VerseAnnotationSerializer,
    VerseHighlightCreateSerializer, VerseHighlightSerializer,
)


class BibleBookListView(generics.ListAPIView):
    queryset = BibleBook.objects.all()
    serializer_class = BibleBookSerializer
    pagination_class = None


class BibleChapterListView(generics.ListAPIView):
    serializer_class = BibleChapterSerializer
    pagination_class = None

    def get_queryset(self):
        return BibleChapter.objects.filter(
            book__slug=self.kwargs['book_slug'],
        ).select_related('book')


class BibleVerseListView(generics.ListAPIView):
    serializer_class = BibleVerseSerializer
    pagination_class = None

    def get_queryset(self):
        return BibleVerse.objects.filter(
            chapter__book__slug=self.kwargs['book_slug'],
            chapter__number=self.kwargs['chapter_num'],
        )


class BibleSearchView(generics.ListAPIView):
    serializer_class = BibleVerseSerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if len(q) < 3:
            return BibleVerse.objects.none()
        return BibleVerse.objects.filter(
            text__icontains=q,
        ).select_related('chapter__book')[:50]


class HighlightCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = HighlightCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return HighlightCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HighlightCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HighlightCategorySerializer

    def get_queryset(self):
        return HighlightCategory.objects.filter(user=self.request.user)


class VerseHighlightListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VerseHighlightCreateSerializer
        return VerseHighlightSerializer

    def get_queryset(self):
        qs = VerseHighlight.objects.filter(
            user=self.request.user,
        ).select_related('start_verse', 'end_verse', 'category', 'annotation')
        chapter_id = self.request.query_params.get('chapter')
        if chapter_id:
            qs = qs.filter(start_verse__chapter_id=chapter_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VerseHighlightDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return VerseHighlight.objects.filter(user=self.request.user)


class AnnotationSaveView(APIView):
    def post(self, request, highlight_id):
        highlight = generics.get_object_or_404(
            VerseHighlight, pk=highlight_id, user=request.user,
        )
        annotation, _ = VerseAnnotation.objects.update_or_create(
            highlight=highlight, user=request.user,
            defaults={'content': request.data.get('content', '')},
        )
        return Response(VerseAnnotationSerializer(annotation).data)


class BibleTagListCreateView(generics.ListCreateAPIView):
    serializer_class = BibleTagSerializer
    pagination_class = None

    def get_queryset(self):
        return BibleTag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BibleTagDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BibleTagSerializer

    def get_queryset(self):
        return BibleTag.objects.filter(user=self.request.user)


class TagAssignView(APIView):
    def post(self, request, highlight_id, tag_id):
        highlight = generics.get_object_or_404(
            VerseHighlight, pk=highlight_id, user=request.user,
        )
        tag = generics.get_object_or_404(BibleTag, pk=tag_id, user=request.user)
        HighlightTag.objects.get_or_create(highlight=highlight, tag=tag)
        return Response({'detail': 'Tag asignado.'})

    def delete(self, request, highlight_id, tag_id):
        HighlightTag.objects.filter(
            highlight_id=highlight_id, tag_id=tag_id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteVerseListView(generics.ListAPIView):
    serializer_class = FavoriteVerseSerializer

    def get_queryset(self):
        return FavoriteVerse.objects.filter(
            user=self.request.user,
        ).select_related('verse__chapter__book')


class FavoriteToggleView(APIView):
    def post(self, request, verse_id):
        verse = generics.get_object_or_404(BibleVerse, pk=verse_id)
        fav, created = FavoriteVerse.objects.get_or_create(
            user=request.user, verse=verse,
        )
        if not created:
            fav.delete()
            return Response({'favorited': False})
        return Response({'favorited': True})


class ReadingProgressView(generics.ListAPIView):
    serializer_class = ReadingProgressSerializer
    pagination_class = None

    def get_queryset(self):
        return ReadingProgress.objects.filter(
            user=self.request.user,
        ).select_related('book', 'chapter')


class SaveReadingProgressView(APIView):
    def post(self, request):
        chapter = generics.get_object_or_404(
            BibleChapter, pk=request.data.get('chapter_id'),
        )
        ReadingProgress.objects.update_or_create(
            user=request.user, book=chapter.book, chapter=chapter,
        )
        return Response({'detail': 'Progreso guardado.'})


class StudyNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyNoteSerializer

    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudyNoteSerializer

    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)
