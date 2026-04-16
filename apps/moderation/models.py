from django.conf import settings
from django.db import models


class BannedWord(models.Model):
    """Palabras prohibidas que se filtran automáticamente."""
    CATEGORY_CHOICES = [
        ('sexual', 'Contenido Sexual'),
        ('insult', 'Insulto'),
        ('violence', 'Violencia'),
        ('drugs', 'Drogas'),
        ('grooming', 'Grooming/Pedofilia'),
        ('spam', 'Spam'),
        ('other', 'Otro'),
    ]
    SEVERITY_CHOICES = [
        ('warn', 'Advertencia'),
        ('block', 'Bloquear'),
        ('ban', 'Ban Automático'),
    ]

    word = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=5, choices=SEVERITY_CHOICES, default='block')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'word']

    def __str__(self):
        return f"{self.word} ({self.get_category_display()})"


class ContentFlag(models.Model):
    """Registro de contenido flaggeado (automático o por reporte)."""
    FLAG_TYPES = [
        ('auto_text', 'Texto Auto-detectado'),
        ('auto_image', 'Imagen Auto-detectada'),
        ('user_report', 'Reporte de Usuario'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('reviewed', 'Revisado'),
        ('dismissed', 'Descartado'),
        ('action_taken', 'Acción Tomada'),
    ]
    CONTENT_TYPE_CHOICES = [
        ('post', 'Publicación'),
        ('comment', 'Comentario'),
        ('message', 'Mensaje'),
        ('story', 'Historia'),
        ('group_post', 'Post de Grupo'),
        ('profile', 'Perfil'),
        ('image', 'Imagen'),
    ]

    flag_type = models.CharField(max_length=12, choices=FLAG_TYPES)
    content_type = models.CharField(max_length=12, choices=CONTENT_TYPE_CHOICES)
    content_id = models.PositiveBigIntegerField()
    flagged_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='content_flags',
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reports_made',
    )
    matched_words = models.TextField(blank=True)
    original_content = models.TextField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='flags_reviewed',
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['flagged_user', '-created_at']),
        ]

    def __str__(self):
        return f"Flag: {self.get_content_type_display()} de {self.flagged_user} ({self.status})"


class ImageReview(models.Model):
    """Cola de revisión de imágenes subidas."""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='image_reviews',
    )
    image_url = models.TextField()
    content_type = models.CharField(max_length=50)
    content_id = models.PositiveBigIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='images_reviewed',
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Imagen de {self.user} ({self.status})"


class UserWarning(models.Model):
    """Advertencias emitidas a usuarios."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='warnings',
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='warnings_issued',
    )
    reason = models.TextField()
    related_flag = models.ForeignKey(
        ContentFlag, on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Advertencia a {self.user}: {self.reason[:50]}"


class UserBan(models.Model):
    """Baneos temporales o permanentes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bans',
    )
    banned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='bans_issued',
    )
    reason = models.TextField()
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        perm = "PERMANENTE" if self.is_permanent else f"hasta {self.expires_at}"
        return f"Ban a {self.user} ({perm})"
