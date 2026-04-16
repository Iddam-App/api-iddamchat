from django.conf import settings
from django.db import models


class ProfilePhoto(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile_photos',
    )
    image = models.ImageField(upload_to='profile_photos/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Foto de {self.user} #{self.order}"


class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='stories',
    )
    image = models.ImageField(upload_to='stories/%Y/%m/%d/', blank=True)
    text = models.CharField(max_length=500, blank=True)
    background_color = models.CharField(max_length=7, default='#2EA3F2')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'stories'

    def __str__(self):
        return f"Historia de {self.user} - {self.created_at:%d/%m}"


class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='viewed_stories',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'viewer')
