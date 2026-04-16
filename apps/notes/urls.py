from django.urls import path

from . import views

app_name = 'notes'

urlpatterns = [
    # Notebooks
    path('notebooks/', views.NotebookListCreateView.as_view(), name='notebook_list'),
    path('notebooks/<int:pk>/', views.NotebookDetailView.as_view(), name='notebook_detail'),

    # Pages
    path('pages/', views.NotePageListCreateView.as_view(), name='page_list'),
    path('pages/<int:pk>/', views.NotePageDetailView.as_view(), name='page_detail'),

    # Images
    path('images/upload/', views.NoteImageUploadView.as_view(), name='image_upload'),

    # Study
    path('study/topics/', views.StudyTopicListCreateView.as_view(), name='study_topics'),
    path('study/topics/<int:pk>/', views.StudyTopicDetailView.as_view(), name='study_topic_detail'),
    path('study/notes/', views.StudyNoteListCreateView.as_view(), name='study_notes'),
    path('study/notes/<int:pk>/', views.StudyNoteDetailView.as_view(), name='study_note_detail'),
]
