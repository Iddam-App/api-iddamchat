from django.urls import path

from . import views

app_name = 'jobs'

urlpatterns = [
    path('categories/', views.JobCategoryListView.as_view(), name='job_categories'),
    path('postings/', views.JobPostingListView.as_view(), name='job_list'),
    path('postings/create/', views.JobPostingCreateView.as_view(), name='job_create'),
    path('postings/<int:pk>/', views.JobPostingDetailView.as_view(), name='job_detail'),
    path('postings/<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='job_delete'),
    path('postings/<int:pk>/bookmark/', views.ToggleBookmarkView.as_view(), name='job_bookmark'),
    path('my-postings/', views.MyJobPostingsView.as_view(), name='my_postings'),
    path('my-bookmarks/', views.MyBookmarksView.as_view(), name='my_bookmarks'),
    path('tip-categories/', views.TipCategoryListView.as_view(), name='tip_categories'),
    path('tips/', views.CareerTipListView.as_view(), name='tip_list'),
    path('tips/create/', views.CareerTipCreateView.as_view(), name='tip_create'),
    path('tips/<int:pk>/', views.CareerTipDetailView.as_view(), name='tip_detail'),
    path('tips/<int:pk>/like/', views.ToggleTipLikeView.as_view(), name='tip_like'),
]
