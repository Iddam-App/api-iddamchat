from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversations/start/', views.ConversationStartView.as_view(), name='conversation_start'),
    path('conversations/<int:conv_id>/messages/', views.MessageListView.as_view(), name='message_list'),
    path('conversations/<int:conv_id>/send/', views.MessageSendView.as_view(), name='message_send'),
    path('unread/', views.UnreadCountView.as_view(), name='unread_count'),
]
