from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Nuevo seguidor'),
        ('follow_request', 'Solicitud de seguimiento'),
        ('follow_request_accepted', 'Solicitud de seguimiento aceptada'),
        ('like', 'Reacción'),
        ('comment', 'Comentario'),
        ('dm_message', 'Mensaje directo'),
        ('friend_request', 'Solicitud de amistad'),
        ('friend_request_accepted', 'Solicitud de amistad aceptada'),
        ('story_reaction', 'Reacción a historia'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    content_type = models.CharField(max_length=50, blank=True)
    content_id = models.PositiveIntegerField(null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.notification_type}"
