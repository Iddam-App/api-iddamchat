from django.conf import settings
from django.db import models


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Texto'),
        ('article', 'Artículo'),
        ('testimony', 'Testimonio'),
        ('news', 'Novedad'),
        ('devotional', 'Devocional'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posts',
    )
    post_type = models.CharField(max_length=15, choices=POST_TYPES, default='text')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_church_official = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"{self.author}: {self.title or self.content[:50]}"

    @property
    def reaction_count(self):
        return self.reactions.count()

    @property
    def comment_count(self):
        return self.comments.count()


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/%Y/%m/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Reaction(models.Model):
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('pray', '🙏'),
        ('amen', '🙌'),
        ('fire', '🔥'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reactions',
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=5, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} → {self.get_reaction_type_display()} en {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='comments',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies',
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author}: {self.content[:50]}"


class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='saved_posts',
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
