from django.urls import path

from . import views

app_name = 'social'

urlpatterns = [
    # Friend requests
    path('friends/request/', views.SendFriendRequestView.as_view(), name='send_request'),
    path('friends/pending/', views.PendingRequestsView.as_view(), name='pending_requests'),
    path('friends/sent/', views.SentRequestsView.as_view(), name='sent_requests'),
    path('friends/request/<int:pk>/<str:action>/', views.RespondFriendRequestView.as_view(), name='respond_request'),
    path('friends/', views.FriendListView.as_view(), name='friend_list'),

    # Follow
    path('follow/<int:user_id>/', views.FollowToggleView.as_view(), name='follow_toggle'),
    path('followers/', views.FollowersListView.as_view(), name='followers'),
    path('following/', views.FollowingListView.as_view(), name='following'),
]
