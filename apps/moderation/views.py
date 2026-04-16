from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import create_flag
from .serializers import ReportContentSerializer


class ReportContentView(APIView):
    """Permite a usuarios reportar contenido inapropiado."""

    def post(self, request):
        serializer = ReportContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Obtener el contenido original para el registro
        original = self._get_content(data['content_type'], data['content_id'])
        if not original:
            return Response(
                {'detail': 'Contenido no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        create_flag(
            user=original['user'],
            content_type=data['content_type'],
            content_id=data['content_id'],
            original_content=original['text'],
            matched_words=[],
            flag_type='user_report',
            reported_by=request.user,
            reason=data['reason'],
        )

        return Response({'detail': 'Reporte enviado. Gracias por ayudar a mantener la comunidad segura.'})

    def _get_content(self, content_type, content_id):
        try:
            if content_type == 'post':
                from apps.posts.models import Post
                obj = Post.objects.get(pk=content_id)
                return {'user': obj.author, 'text': obj.content}
            elif content_type == 'comment':
                from apps.posts.models import Comment
                obj = Comment.objects.get(pk=content_id)
                return {'user': obj.author, 'text': obj.content}
            elif content_type == 'message':
                from apps.chat.models import Message
                obj = Message.objects.get(pk=content_id)
                return {'user': obj.sender, 'text': obj.content}
            elif content_type == 'story':
                from apps.profiles.models import Story
                obj = Story.objects.get(pk=content_id)
                return {'user': obj.user, 'text': obj.text}
            elif content_type == 'group_post':
                from apps.groups.models import GroupPost
                obj = GroupPost.objects.get(pk=content_id)
                return {'user': obj.author, 'text': obj.content}
            elif content_type == 'profile':
                from django.contrib.auth import get_user_model
                obj = get_user_model().objects.get(pk=content_id)
                return {'user': obj, 'text': obj.bio}
        except Exception:
            return None
        return None
