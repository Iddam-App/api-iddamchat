from django.urls import path

from . import views

app_name = 'hosting'

urlpatterns = [
    path('hosts/', views.HostProfileListView.as_view(), name='host_list'),
    path('my-profile/', views.MyHostProfileView.as_view(), name='my_host_profile'),
    path('request/', views.HostingRequestCreateView.as_view(), name='request_create'),
    path('my-requests/', views.MyHostingRequestsView.as_view(), name='my_requests'),
    path('received/', views.ReceivedHostingRequestsView.as_view(), name='received_requests'),
    path('request/<int:pk>/<str:action>/', views.RespondHostingRequestView.as_view(), name='respond_request'),
    path('request/<int:pk>/message/', views.HostingMessageCreateView.as_view(), name='send_message'),
]
