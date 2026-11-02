from django.conf import settings
from django.db import models


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Job categories'

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Medio tiempo'),
        ('contract', 'Contrato'),
        ('freelance', 'Freelance'),
        ('internship', 'Pasantia'),
        ('volunteer', 'Voluntariado'),
    ]
    MODALITY_CHOICES = [
        ('on_site', 'Presencial'),
        ('remote', 'Remoto'),
        ('hybrid', 'Hibrido'),
    ]
    EXPERIENCE_CHOICES = [
        ('entry', 'Junior'),
        ('mid', 'Intermedio'),
        ('senior', 'Senior'),
        ('any', 'No importa'),
    ]
    SALARY_TYPE_CHOICES = [
        ('range', 'Rango salarial'),
        ('negotiable', 'A convenir'),
        ('contact', 'Contactar personalmente'),
        ('volunteer', 'Voluntariado / Sin remuneracion'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='job_postings',
    )
    title = models.CharField('Titulo del puesto', max_length=200)
    description = models.TextField('Descripcion del trabajo')
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='postings',
    )
    company_name = models.CharField('Empresa', max_length=150, blank=True)
    job_type = models.CharField(
        max_length=15, choices=JOB_TYPE_CHOICES, default='full_time',
    )
    modality = models.CharField(
        max_length=10, choices=MODALITY_CHOICES, default='on_site',
    )
    experience_level = models.CharField(
        max_length=10, choices=EXPERIENCE_CHOICES, default='any',
    )
    salary_type = models.CharField(
        max_length=15, choices=SALARY_TYPE_CHOICES, default='negotiable',
    )
    location_city = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=5, blank=True)
    skills = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=5, default='USD')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='jobs/%Y/%m/', blank=True)
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} — {self.company_name or self.author}"


class JobBookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='job_bookmarks',
    )
    job = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user} → {self.job}"


class TipCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children',
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Tip categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class CareerTip(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='career_tips',
    )
    category = models.ForeignKey(
        TipCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tips',
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='tips/%Y/%m/', blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TipLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='tip_likes',
    )
    tip = models.ForeignKey(
        CareerTip, on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tip')

    def __str__(self):
        return f"{self.user} likes {self.tip}"
