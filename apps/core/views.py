from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserLanguage
from .serializers import (
    ChangePasswordSerializer, RegisterSerializer, UserLanguageSerializer,
    UserMinimalSerializer, UserSerializer, UserSuggestionSerializer,
)

User = get_user_model()


def _is_following(user, target):
    """Check if user follows target."""
    from apps.social.models import Follow
    return Follow.objects.filter(follower=user, followed=target).exists()


def _annotate_mutual_names(request_user, users):
    """Attach _mutual_names (list of up to 2 display names) to each user."""
    from apps.social.models import Follow

    my_following_ids = set(
        Follow.objects.filter(follower=request_user)
        .values_list('followed_id', flat=True)
    )
    if not my_following_ids:
        for u in users:
            u._mutual_names = []
        return users

    user_ids = [u.pk for u in users]
    # Get all follows where one of my followed users follows one of the result users
    mutual_qs = (
        Follow.objects.filter(
            follower_id__in=my_following_ids,
            followed_id__in=user_ids,
        )
        .select_related('follower')
    )
    # Group by followed_id
    mutual_map = {}  # followed_id -> [follower display names]
    for f in mutual_qs:
        names = mutual_map.setdefault(f.followed_id, [])
        if len(names) < 2:
            name = (
                f.follower.nickname
                or f.follower.first_name
                or f.follower.username
            )
            names.append(name)

    for u in users:
        u._mutual_names = mutual_map.get(u.pk, [])
    return users


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
    serializer_class = UserSuggestionSerializer

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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = _annotate_mutual_names(request.user, queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserSuggestionsView(generics.ListAPIView):
    """Suggest users the current user is NOT following yet.
    Prioritizes friends-of-friends and annotates mutual follow names.
    """
    serializer_class = UserSuggestionSerializer
    pagination_class = None

    def get_queryset(self):
        from apps.social.models import Follow
        from django.db.models import Count

        user = self.request.user
        my_following_ids = set(
            Follow.objects.filter(follower=user)
            .values_list('followed_id', flat=True)
        )
        exclude_ids = my_following_ids | {user.pk}

        # Friends of friends: users followed by people I follow, that I don't follow
        fof = (
            User.objects.filter(
                is_active=True,
                followers__follower_id__in=my_following_ids,
            )
            .exclude(pk__in=exclude_ids)
            .annotate(mutual_count=Count('followers', filter=Q(
                followers__follower_id__in=my_following_ids,
            )))
            .order_by('-mutual_count', '?')[:12]
        )
        fof_list = list(fof)

        # Fill with random users if we have fewer than 12
        if len(fof_list) < 12:
            fof_ids = {u.pk for u in fof_list}
            remaining = 12 - len(fof_list)
            fillers = list(
                User.objects.filter(is_active=True)
                .exclude(pk__in=exclude_ids | fof_ids)
                .order_by('?')[:remaining]
            )
            # Set mutual_count=0 for fillers
            for u in fillers:
                u.mutual_count = 0
            fof_list.extend(fillers)

        return fof_list

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        users = _annotate_mutual_names(request.user, users)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


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


class BadgesView(APIView):
    """Single endpoint for all nav badge counts (unread msgs + notifications)."""

    def get(self, request):
        from django.db.models import Exists, OuterRef
        from apps.chat.models import Conversation, Message
        from apps.notifications.models import Notification

        user = request.user
        unread_messages = Conversation.objects.filter(
            Q(user1=user) | Q(user2=user),
        ).filter(
            Exists(
                Message.objects.filter(
                    conversation=OuterRef('pk'),
                    is_read=False,
                ).exclude(sender=user)
            )
        ).count()

        unread_notifs = Notification.objects.filter(
            recipient=user, is_read=False,
        ).count()

        return Response({
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifs,
        })


class AvailableLanguagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .constants import AVAILABLE_LANGUAGES
        return Response(AVAILABLE_LANGUAGES)


class InitDemoInteractionsView(APIView):
    """Create demo followers + welcome conversations for the current user."""

    def post(self, request):
        from datetime import timedelta
        from apps.social.models import Follow
        from apps.chat.models import Conversation, Message

        DEMO_DOMAIN = 'demo.iddam.app'
        FOLLOWERS = [
            'matias@demo.iddam.app',
            'daniela@demo.iddam.app',
            'lucas@demo.iddam.app',
            'david@demo.iddam.app',
            'genesis@demo.iddam.app',
            'pablo@demo.iddam.app',
        ]
        CONVERSATIONS = [
            {
                'sender': 'matias@demo.iddam.app',
                'messages': [
                    'Hola! Bienvenido a IddamChat! Soy Matías, de Santiago de Chile.',
                    'Espero que te guste la app. Cualquier cosa que necesites, aquí estamos!',
                ],
            },
            {
                'sender': 'david@demo.iddam.app',
                'messages': [
                    'Hey! Welcome to IddamChat! I am David from Dallas.',
                    'Feel free to check out the groups and events. See you around!',
                ],
            },
            {
                'sender': 'daniela@demo.iddam.app',
                'messages': [
                    'Holaa! Soy Daniela, bienvenido/a!',
                    'Si te gusta el diseño o quieres compartir algo creativo, este es tu lugar.',
                ],
            },
        ]

        user = request.user
        now = timezone.now()
        created_follows = 0
        created_convs = 0
        created_msgs = 0

        # Follows
        for email in FOLLOWERS:
            try:
                demo = User.objects.get(email=email)
                _, created = Follow.objects.get_or_create(
                    follower=demo, followed=user,
                )
                if created:
                    created_follows += 1
            except User.DoesNotExist:
                continue

        # Conversations
        for conv_data in CONVERSATIONS:
            try:
                sender = User.objects.get(email=conv_data['sender'])
            except User.DoesNotExist:
                continue
            u1 = min(sender, user, key=lambda u: u.pk)
            u2 = max(sender, user, key=lambda u: u.pk)
            conv, was_new = Conversation.objects.get_or_create(
                user1=u1, user2=u2,
            )
            if was_new:
                created_convs += 1
                for j, content in enumerate(conv_data['messages']):
                    msg = Message.objects.create(
                        conversation=conv,
                        sender=sender,
                        content=content,
                    )
                    Message.objects.filter(pk=msg.pk).update(
                        created_at=now - timedelta(
                            hours=len(conv_data['messages']) - j,
                        ),
                    )
                    created_msgs += 1

        return Response({
            'created_follows': created_follows,
            'created_conversations': created_convs,
            'created_messages': created_msgs,
            'total_followers': Follow.objects.filter(followed=user).count(),
            'total_conversations': Conversation.objects.filter(
                Q(user1=user) | Q(user2=user),
            ).count(),
        })
