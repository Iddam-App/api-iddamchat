from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'content',
            'was_filtered', 'image', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'conversation', 'sender', 'was_filtered',
            'is_read', 'read_at', 'created_at',
        ]


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_user', 'last_message', 'unread_count',
                  'created_at', 'updated_at']

    def get_other_user(self, obj):
        request = self.context['request']
        other = obj.user2 if obj.user1 == request.user else obj.user1
        return UserMinimalSerializer(other, context=self.context).data

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {
                'content': msg.content[:100],
                'sender_id': msg.sender_id,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context['request']
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
