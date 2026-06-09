from django.urls import path

from . import views

app_name = 'bible'

urlpatterns = [
    # Read-only Bible data
    path('books/', views.BibleBookListView.as_view(), name='book_list'),
    path('books/<slug:book_slug>/chapters/', views.BibleChapterListView.as_view(), name='chapter_list'),
    path('books/<slug:book_slug>/<int:chapter_num>/verses/', views.BibleVerseListView.as_view(), name='verse_list'),
    path('search/', views.BibleSearchView.as_view(), name='search'),

    # Highlights
    path('categories/', views.HighlightCategoryListCreateView.as_view(), name='categories'),
    path('categories/<int:pk>/', views.HighlightCategoryDetailView.as_view(), name='category_detail'),
    path('highlights/', views.VerseHighlightListCreateView.as_view(), name='highlights'),
    path('highlights/<int:pk>/', views.VerseHighlightDeleteView.as_view(), name='highlight_delete'),

    # Annotations
    path('highlights/<int:highlight_id>/annotation/', views.AnnotationSaveView.as_view(), name='annotation'),

    # Tags
    path('tags/', views.BibleTagListCreateView.as_view(), name='tags'),
    path('tags/<int:pk>/', views.BibleTagDetailView.as_view(), name='tag_detail'),
    path('highlights/<int:highlight_id>/tags/<int:tag_id>/', views.TagAssignView.as_view(), name='tag_assign'),

    # Favorites
    path('favorites/', views.FavoriteVerseListView.as_view(), name='favorites'),
    path('favorites/<int:verse_id>/', views.FavoriteToggleView.as_view(), name='favorite_toggle'),

    # Progress
    path('progress/', views.ReadingProgressView.as_view(), name='progress'),
    path('progress/save/', views.SaveReadingProgressView.as_view(), name='save_progress'),

    # Study notes
    path('study-notes/', views.StudyNoteListCreateView.as_view(), name='study_notes'),
    path('study-notes/<int:pk>/', views.StudyNoteDetailView.as_view(), name='study_note_detail'),

    # Study Folders
    path('folders/', views.StudyFolderListCreateView.as_view(), name='study_folders'),
    path('folders/<int:pk>/', views.StudyFolderDetailView.as_view(), name='study_folder_detail'),

    # Study Books / PDF
    path('books-study/', views.StudyBookListCreateView.as_view(), name='study_book_list'),
    path('books-study/<int:pk>/', views.StudyBookDetailView.as_view(), name='study_book_detail'),
    path('books-study/<int:pk>/upload-pdf/', views.StudyBookUploadPDFView.as_view(), name='study_book_upload_pdf'),
    path('books-study/<int:pk>/pdf/', views.StudyBookPDFView.as_view(), name='study_book_pdf'),
    path('books-study/<int:pk>/reading-logs/', views.BookReadingLogListCreateView.as_view(), name='book_reading_logs'),
    path('books-study/<int:pk>/page-notes/', views.BookPageNoteListCreateView.as_view(), name='book_page_notes'),
    path('books-study/page-notes/<int:pk>/', views.BookPageNoteDetailView.as_view(), name='book_page_note_detail'),
    path('books-study/<int:pk>/highlights/', views.BookHighlightListCreateView.as_view(), name='book_highlights'),
    path('books-study/highlights/<int:pk>/', views.BookHighlightDetailView.as_view(), name='book_highlight_detail'),
    path('books-study/<int:pk>/subtitles/', views.BookSubtitleListCreateView.as_view(), name='book_subtitles'),
    path('books-study/subtitles/<int:pk>/', views.BookSubtitleDeleteView.as_view(), name='book_subtitle_delete'),
]
