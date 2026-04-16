from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.GroupListCreateView.as_view(), name='group_list'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<int:pk>/members/', views.GroupMembersView.as_view(), name='group_members'),
    path('<int:pk>/join/', views.JoinGroupView.as_view(), name='join_group'),
    path('<int:pk>/leave/', views.LeaveGroupView.as_view(), name='leave_group'),
    path('<int:pk>/requests/', views.GroupJoinRequestsView.as_view(), name='join_requests'),
    path('requests/<int:pk>/<str:action>/', views.RespondJoinRequestView.as_view(), name='respond_join'),
    path('<int:pk>/posts/', views.GroupPostListCreateView.as_view(), name='group_posts'),

    # Proposals
    path('proposals/', views.ProposalListCreateView.as_view(), name='proposals'),
    path('proposals/<int:pk>/join/', views.ProposalJoinView.as_view(), name='proposal_join'),
]
