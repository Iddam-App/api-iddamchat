from django.conf import settings
from django.db import models


class Podcast(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_url = models.URLField()
    cover_image = models.ImageField(upload_to='podcasts/covers/', blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    episode_number = models.PositiveIntegerField(null=True, blank=True)
    series = models.CharField(max_length=100, blank=True)
    external_url = models.URLField(blank=True)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('god', 'Dios'),
        ('bible', 'Biblia'),
        ('life', 'Vida'),
        ('prophecy', 'Profecía'),
        ('change', 'Cambio'),
        ('relationships', 'Relaciones'),
        ('youth', 'Jóvenes'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    author_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, blank=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    cover_image = models.ImageField(upload_to='articles/covers/', blank=True)
    external_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class ChurchService(models.Model):
    SERVICE_TYPES = [
        ('webcast', 'Webcast'),
        ('sermon', 'Sermón'),
        ('bible_study', 'Estudio Bíblico'),
        ('special', 'Especial'),
    ]

    title = models.CharField(max_length=255)
    service_type = models.CharField(max_length=12, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    speaker = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date}"


class SavedContent(models.Model):
    CONTENT_TYPES = [
        ('podcast', 'Podcast'),
        ('article', 'Artículo'),
        ('service', 'Servicio'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='saved_content',
    )
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    podcast = models.ForeignKey(
        Podcast, on_delete=models.CASCADE, null=True, blank=True,
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True,
    )
    service = models.ForeignKey(
        ChurchService, on_delete=models.CASCADE, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} guardó {self.content_type}"
