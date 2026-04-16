from django.conf import settings
from django.db import models


class Notebook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notebooks',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children',
    )
    title = models.CharField(max_length=200, default='Sin título')
    icon = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=7, default='#2EA3F2')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-updated_at']

    def __str__(self):
        return self.title

    @property
    def page_count(self):
        return self.pages.count()


class NotePage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='note_pages',
    )
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, null=True, blank=True,
        related_name='pages',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subpages',
    )
    title = models.CharField(max_length=200, default='Sin título')
    icon = models.CharField(max_length=10, blank=True)
    cover_image = models.ImageField(upload_to='note_covers/', blank=True)
    content = models.JSONField(default=dict, blank=True)
    excerpt = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-updated_at']

    def __str__(self):
        return self.title


class NoteImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='note_images',
    )
    page = models.ForeignKey(
        NotePage, on_delete=models.CASCADE, null=True, blank=True,
        related_name='images',
    )
    image = models.ImageField(upload_to='note_images/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class StudyTopic(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='study_topics',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=7, default='#2EA3F2')
    cover_image = models.ImageField(upload_to='study_covers/', blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class StudyNote(models.Model):
    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='notes',
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
