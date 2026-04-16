from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = 'core'

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('me/password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Users
    path('users/search/', views.UserSearchView.as_view(), name='user_search'),
    path('users/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
]
