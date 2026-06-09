from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.filter import check_and_flag
from apps.notifications.services import create_notification

from .models import Conversation, Message, MessageTranslation
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        from django.db.models import Prefetch
        return Conversation.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user),
        ).select_related('user1', 'user2').prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-created_at'),
            ),
        )


class ConversationStartView(APIView):
    def post(self, request):
        other_id = request.data.get('user_id')
        other = generics.get_object_or_404(User, pk=other_id, is_active=True)

        if other == request.user:
            return Response(
                {'detail': 'No puedes chatear contigo mismo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Orden consistente para evitar duplicados
        u1 = min(request.user, other, key=lambda u: u.pk)
        u2 = max(request.user, other, key=lambda u: u.pk)

        conv, created = Conversation.objects.get_or_create(user1=u1, user2=u2)
        return Response(
            ConversationSerializer(conv, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conv = generics.get_object_or_404(
            Conversation, pk=self.kwargs['conv_id'],
        )
        user = self.request.user
        if user not in (conv.user1, conv.user2):
            return Message.objects.none()

        # Marcar como leídos los mensajes del otro usuario
        conv.messages.filter(is_read=False).exclude(
            sender=user,
        ).update(is_read=True, read_at=timezone.now())

        return conv.messages.select_related('sender').all()


class MessageSendView(APIView):
    def post(self, request, conv_id):
        conv = generics.get_object_or_404(Conversation, pk=conv_id)
        user = request.user

        if user not in (conv.user1, conv.user2):
            return Response(
                {'detail': 'No autorizado.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        content = request.data.get('content', '').strip()
        image = request.FILES.get('image')
        confirmed = request.data.get('confirmed', False)

        if not content and not image:
            return Response(
                {'detail': 'El mensaje no puede estar vacío.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filtro de contenido
        was_filtered = False

        if content:
            mod_result = check_and_flag(
                user=user,
                text=content,
                content_type='message',
                content_id=0,
                confirmed=confirmed,
            )

            # Ban automático (grooming)
            if mod_result['severity'] == 'ban':
                return Response({
                    'detail': mod_result['warning_message'],
                    'severity': 'ban',
                }, status=status.HTTP_403_FORBIDDEN)

            # Necesita confirmación → el frontend muestra "No diga esas cosas"
            if mod_result['needs_confirmation']:
                return Response({
                    'detail': mod_result['warning_message'],
                    'needs_confirmation': True,
                    'severity': mod_result['severity'],
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Si confirmed=True, el mensaje pasa pero queda alerta al admin
            if mod_result['severity']:
                was_filtered = True

        msg = Message.objects.create(
            conversation=conv,
            sender=user,
            content=content,
            original_content=content if was_filtered else '',
            was_filtered=was_filtered,
            image=image or '',
        )

        conv.save(update_fields=['updated_at'])

        # Notify the other user
        other_user = conv.user2 if conv.user1 == user else conv.user1
        create_notification(
            recipient=other_user, sender=user,
            notification_type='dm_message',
            message=f'{user.display_name} te envió un mensaje.',
            content_type='conversation', content_id=conv.pk,
        )

        return Response(
            MessageSerializer(msg, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class UnreadCountView(APIView):
    def get(self, request):
        count = Message.objects.filter(
            conversation__in=Conversation.objects.filter(
                Q(user1=request.user) | Q(user2=request.user),
            ),
            is_read=False,
        ).exclude(sender=request.user).count()
        return Response({'unread_count': count})


class TranslateMessageView(APIView):
    def post(self, request, message_id):
        msg = generics.get_object_or_404(Message, pk=message_id)
        conv = msg.conversation
        user = request.user

        # Verify user is part of the conversation
        if user not in (conv.user1, conv.user2):
            return Response(
                {'detail': 'No autorizado.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        target_language = request.data.get(
            'target_language', user.preferred_language or 'es',
        )

        # Check cache
        cached = MessageTranslation.objects.filter(
            message=msg, target_language=target_language,
        ).first()
        if cached:
            return Response({
                'translated_text': cached.translated_text,
                'source_language': cached.source_language,
                'target_language': target_language,
                'cached': True,
            })

        # Translate
        from .translation import translate_text
        try:
            result = translate_text(msg.content, target_language)
        except Exception as e:
            return Response(
                {'detail': f'Error de traducción: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Cache the translation
        translation = MessageTranslation.objects.create(
            message=msg,
            target_language=target_language,
            translated_text=result['translated_text'],
            source_language=result['detected_source_language'],
        )

        return Response({
            'translated_text': translation.translated_text,
            'source_language': translation.source_language,
            'target_language': target_language,
            'cached': False,
        })
