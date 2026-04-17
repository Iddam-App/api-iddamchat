from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/react/', views.ReactView.as_view(), name='react'),
    path('<int:pk>/comments/', views.CommentListCreateView.as_view(), name='comments'),
    path('<int:pk>/save/', views.SavePostToggleView.as_view(), name='save_post'),
    path('saved/', views.SavedPostsView.as_view(), name='saved_posts'),
    path('user/<int:user_id>/', views.UserPostsView.as_view(), name='user_posts'),
    path('hobbies/', views.HobbiesFeedView.as_view(), name='hobbies_feed'),
    path('<int:pk>/hide/', views.ToggleHidePostView.as_view(), name='toggle_hide'),
]
