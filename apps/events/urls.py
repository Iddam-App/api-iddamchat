from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListCreateView.as_view(), name='event_list'),
    path('mine/', views.MyEventsView.as_view(), name='my_events'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/rsvp/', views.EventRSVPView.as_view(), name='event_rsvp'),
    path('<int:pk>/attendees/', views.EventAttendeesView.as_view(), name='attendees'),
]
