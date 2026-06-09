from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserLanguage
from .serializers import (
    ChangePasswordSerializer, RegisterSerializer, UserLanguageSerializer,
    UserMinimalSerializer, UserSerializer,
)

User = get_user_model()


def _is_following(user, target):
    """Check if user follows target."""
    from apps.social.models import Follow
    return Follow.objects.filter(follower=user, followed=target).exists()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        bio = serializer.validated_data.get('bio', '')
        if bio:
            from apps.moderation.filter import check_and_flag
            confirmed = request.data.get('confirmed', False)
            mod_result = check_and_flag(
                user=request.user, text=bio,
                content_type='profile', content_id=request.user.pk,
                confirmed=confirmed,
            )
            if mod_result['severity'] == 'ban':
                return Response({
                    'detail': mod_result['warning_message'],
                    'severity': 'ban',
                }, status=403)
            if mod_result['needs_confirmation']:
                return Response({
                    'detail': mod_result['warning_message'],
                    'needs_confirmation': True,
                }, status=422)

        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Contraseña actualizada.'})


class DeleteAccountView(APIView):
    def post(self, request):
        password = request.data.get('password', '')
        if not password:
            return Response(
                {'detail': 'Debes confirmar tu contraseña.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(password):
            return Response(
                {'detail': 'Contraseña incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])
        return Response({'detail': 'Cuenta eliminada.'})


class UserSearchView(generics.ListAPIView):
    serializer_class = UserMinimalSerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if len(q) < 2:
            return User.objects.none()
        return User.objects.filter(
            is_active=True,
        ).filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(nickname__icontains=q) |
            Q(username__icontains=q) |
            Q(congregation__icontains=q),
        ).exclude(pk=self.request.user.pk)[:20]


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()

        # If private and not following, return limited info
        if user.is_private and user != request.user and not _is_following(request.user, user):
            return Response({
                'id': user.pk,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'nickname': user.nickname,
                'avatar': user.avatar.url if user.avatar else None,
                'country': user.country,
                'display_name': user.display_name,
                'is_private': True,
                'is_restricted': True,
            })

        serializer = self.get_serializer(user)
        return Response(serializer.data)


# ─── Language Views ────────────────────────────────────────────────

class UserLanguageListCreateView(generics.ListCreateAPIView):
    serializer_class = UserLanguageSerializer
    pagination_class = None

    def get_queryset(self):
        return UserLanguage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserLanguageDeleteView(generics.DestroyAPIView):
    serializer_class = UserLanguageSerializer

    def get_queryset(self):
        return UserLanguage.objects.filter(user=self.request.user)


class AvailableLanguagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .constants import AVAILABLE_LANGUAGES
        return Response(AVAILABLE_LANGUAGES)
