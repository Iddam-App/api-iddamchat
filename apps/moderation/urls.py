from django.urls import path

from . import views

app_name = 'moderation'

urlpatterns = [
    path('report/', views.ReportContentView.as_view(), name='report'),
]
