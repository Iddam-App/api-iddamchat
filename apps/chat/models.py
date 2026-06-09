from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """Conversación entre dos usuarios."""
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='conversations_as_user1',
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='conversations_as_user2',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.user1} ↔ {self.user2}"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """Mensaje individual en una conversación."""
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    content = models.TextField()
    # Contenido original si fue censurado
    original_content = models.TextField(blank=True)
    was_filtered = models.BooleanField(default=False)
    matched_words = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat/images/%Y/%m/', blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}"


class MessageTranslation(models.Model):
    """Cached translation of a message."""
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='translations',
    )
    target_language = models.CharField(max_length=10)
    translated_text = models.TextField()
    source_language = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'target_language')

    def __str__(self):
        return f"Translation of msg {self.message_id} to {self.target_language}"
