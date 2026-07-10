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
    path('stories/user/<int:user_id>/', views.UserStoriesView.as_view(), name='user_stories'),

    # Highlights
    path('highlights/', views.StoryHighlightListCreateView.as_view(), name='highlight_list'),
    path('highlights/user/<int:user_id>/', views.StoryHighlightListCreateView.as_view(), name='highlight_list_user'),
    path('highlights/<int:pk>/', views.StoryHighlightDetailView.as_view(), name='highlight_detail'),
    path('highlights/<int:pk>/add/', views.StoryHighlightAddItemView.as_view(), name='highlight_add_item'),
    path('highlights/<int:pk>/items/<int:item_id>/', views.StoryHighlightRemoveItemView.as_view(), name='highlight_remove_item'),
]
