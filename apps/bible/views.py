from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BibleBook, BibleChapter, BibleTag, BibleVerse,
    BookHighlight, BookPageNote, BookReadingLog, BookSubtitle,
    FavoriteVerse, HighlightCategory, HighlightTag,
    ReadingProgress, StudyBook, StudyFolder, StudyNote,
    VerseAnnotation, VerseHighlight,
)
from .serializers import (
    BibleBookSerializer, BibleChapterSerializer, BibleTagSerializer,
    BibleVerseSerializer, BookHighlightSerializer, BookPageNoteSerializer,
    BookReadingLogSerializer, BookSubtitleSerializer, FavoriteVerseSerializer,
    HighlightCategorySerializer, ReadingProgressSerializer,
    StudyBookDetailSerializer, StudyBookSerializer, StudyFolderSerializer,
    StudyNoteSerializer, VerseAnnotationSerializer,
    VerseHighlightCreateSerializer, VerseHighlightSerializer,
)


# ─── Bible Read-Only Views ─────────────────────────────────────────

@method_decorator(cache_page(60 * 60), name='dispatch')  # 1 hour cache
class BibleBookListView(generics.ListAPIView):
    queryset = BibleBook.objects.all()
    serializer_class = BibleBookSerializer
    pagination_class = None


@method_decorator(cache_page(60 * 60), name='dispatch')
class BibleChapterListView(generics.ListAPIView):
    serializer_class = BibleChapterSerializer
    pagination_class = None

    def get_queryset(self):
        return BibleChapter.objects.filter(
            book__slug=self.kwargs['book_slug'],
        ).select_related('book')


@method_decorator(cache_page(60 * 60), name='dispatch')
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


# ─── Highlight Categories ──────────────────────────────────────────

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


# ─── Verse Highlights ──────────────────────────────────────────────

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


# ─── Annotations ───────────────────────────────────────────────────

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


# ─── Tags ──────────────────────────────────────────────────────────

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


# ─── Favorites ─────────────────────────────────────────────────────

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


# ─── Reading Progress ─────────────────────────────────────────────

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


# ─── Study Notes ───────────────────────────────────────────────────

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


# ─── Study Folders ─────────────────────────────────────────────────

class StudyFolderListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyFolderSerializer
    pagination_class = None

    def get_queryset(self):
        return StudyFolder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyFolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudyFolderSerializer

    def get_queryset(self):
        return StudyFolder.objects.filter(user=self.request.user)


# ─── Study Books / PDF ─────────────────────────────────────────────

class StudyBookListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyBookSerializer

    def get_queryset(self):
        return StudyBook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudyBookDetailSerializer

    def get_queryset(self):
        return StudyBook.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Delete PDF from R2 if exists
        if instance.pdf_key:
            try:
                from .r2_storage import delete_file_from_r2
                delete_file_from_r2(instance.pdf_key)
            except Exception:
                pass
        instance.delete()


class StudyBookUploadPDFView(APIView):
    def post(self, request, pk):
        book = generics.get_object_or_404(StudyBook, pk=pk, user=request.user)
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return Response(
                {'detail': 'No se proporcionó archivo PDF.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Count pages
        total_pages = 0
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_file)
            total_pages = len(reader.pages)
        except Exception:
            pass

        # Reset file position after reading
        pdf_file.seek(0)

        # Upload to R2
        from .r2_storage import upload_file_to_r2
        key = f'books/{request.user.pk}/{book.pk}/{pdf_file.name}'

        # Delete old PDF if exists
        if book.pdf_key:
            try:
                from .r2_storage import delete_file_from_r2
                delete_file_from_r2(book.pdf_key)
            except Exception:
                pass

        upload_file_to_r2(pdf_file, key)

        book.pdf_key = key
        book.pdf_filename = pdf_file.name
        if total_pages > 0:
            book.total_pages = total_pages
        book.save(update_fields=['pdf_key', 'pdf_filename', 'total_pages', 'updated_at'])

        return Response(StudyBookSerializer(book).data)


class StudyBookPDFView(APIView):
    def get(self, request, pk):
        book = generics.get_object_or_404(StudyBook, pk=pk, user=request.user)
        if not book.pdf_key:
            return Response(
                {'detail': 'Este libro no tiene PDF.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        from .r2_storage import get_presigned_url
        url = get_presigned_url(book.pdf_key)
        return HttpResponseRedirect(url)


# ─── Book Reading Logs ─────────────────────────────────────────────

class BookReadingLogListCreateView(generics.ListCreateAPIView):
    serializer_class = BookReadingLogSerializer
    pagination_class = None

    def get_queryset(self):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        return book.reading_logs.all()

    def perform_create(self, serializer):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        log = serializer.save(book=book)
        # Update current page
        if log.page_end > book.current_page:
            book.current_page = log.page_end
            book.save(update_fields=['current_page', 'updated_at'])


# ─── Book Page Notes ──────────────────────────────────────────────

class BookPageNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = BookPageNoteSerializer

    def get_queryset(self):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        return book.page_notes.all()

    def perform_create(self, serializer):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        serializer.save(book=book)


class BookPageNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookPageNoteSerializer

    def get_queryset(self):
        return BookPageNote.objects.filter(book__user=self.request.user)


# ─── Book Highlights ──────────────────────────────────────────────

class BookHighlightListCreateView(generics.ListCreateAPIView):
    serializer_class = BookHighlightSerializer

    def get_queryset(self):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        return book.highlights.all()

    def perform_create(self, serializer):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        serializer.save(book=book)


class BookHighlightDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookHighlightSerializer

    def get_queryset(self):
        return BookHighlight.objects.filter(book__user=self.request.user)


# ─── Book Subtitles ───────────────────────────────────────────────

class BookSubtitleListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSubtitleSerializer
    pagination_class = None

    def get_queryset(self):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        return book.subtitles.all()

    def perform_create(self, serializer):
        book = generics.get_object_or_404(
            StudyBook, pk=self.kwargs['pk'], user=self.request.user,
        )
        serializer.save(book=book)


class BookSubtitleDeleteView(generics.DestroyAPIView):

    def get_queryset(self):
        return BookSubtitle.objects.filter(book__user=self.request.user)
