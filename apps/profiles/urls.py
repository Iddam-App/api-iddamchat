from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    # Photos
    path('photos/', views.ProfilePhotoListCreateView.as_view(), name='photo_list'),
    path('photos/<int:pk>/', views.ProfilePhotoDeleteView.as_view(), name='photo_delete'),

    # Stories
    path('stories/feed/', views.StoryFeedView.as_view(), name='story_feed'),
    path('stories/create/', views.StoryCreateView.as_view(), name='story_create'),
    path('stories/mine/', views.MyStoriesView.as_view(), name='my_stories'),
    path('stories/<int:pk>/view/', views.StoryViewRegister.as_view(), name='story_view'),
]
