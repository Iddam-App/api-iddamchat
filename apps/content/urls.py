from django.urls import path

from . import views

app_name = 'content'

urlpatterns = [
    # Podcasts
    path('podcasts/', views.PodcastListView.as_view(), name='podcast_list'),
    path('podcasts/<int:pk>/', views.PodcastDetailView.as_view(), name='podcast_detail'),

    # Articles
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),

    # Church services
    path('services/', views.ChurchServiceListView.as_view(), name='service_list'),
    path('services/<int:pk>/', views.ChurchServiceDetailView.as_view(), name='service_detail'),

    # Saved content
    path('save/', views.SaveContentView.as_view(), name='save_content'),
    path('saved/', views.SavedContentListView.as_view(), name='saved_list'),
]
