from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'content_type',
            'content_id', 'message', 'is_read', 'created_at',
        ]
        read_only_fields = fields
