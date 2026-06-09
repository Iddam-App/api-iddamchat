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
    path('me/delete/', views.DeleteAccountView.as_view(), name='delete_account'),

    # Languages
    path('me/languages/', views.UserLanguageListCreateView.as_view(), name='user_languages'),
    path('me/languages/<int:pk>/', views.UserLanguageDeleteView.as_view(), name='user_language_delete'),
    path('languages/', views.AvailableLanguagesView.as_view(), name='available_languages'),

    # Users
    path('users/search/', views.UserSearchView.as_view(), name='user_search'),
    path('users/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
]
