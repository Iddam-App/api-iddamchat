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


class ProfessionalProfile(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Disponible'),
        ('busy', 'Ocupado'),
        ('not_looking', 'No busco trabajo'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'USD'), ('EUR', 'EUR'), ('MXN', 'MXN'),
        ('CLP', 'CLP'), ('ARS', 'ARS'), ('COP', 'COP'),
        ('PEN', 'PEN'), ('BRL', 'BRL'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='professional_profile',
    )
    headline = models.CharField('Titulo profesional', max_length=200)
    summary = models.TextField('Resumen profesional', max_length=2000, blank=True)
    availability = models.CharField(
        max_length=15, choices=AVAILABILITY_CHOICES, default='available',
    )
    years_of_experience = models.PositiveSmallIntegerField(
        'Anos de experiencia', null=True, blank=True,
    )
    education = models.CharField('Educacion', max_length=200, blank=True)
    skills = models.TextField('Habilidades', blank=True)
    services = models.TextField('Servicios ofrecidos', blank=True)
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='professionals',
    )
    hourly_rate = models.PositiveIntegerField(
        'Tarifa por hora', null=True, blank=True,
    )
    rate_currency = models.CharField(
        max_length=5, choices=CURRENCY_CHOICES, default='USD',
    )
    linkedin_url = models.URLField('LinkedIn', blank=True)
    github_url = models.URLField('GitHub', blank=True)
    portfolio_url = models.URLField('Portafolio', blank=True)
    other_url = models.URLField('Otro enlace', blank=True)
    is_public = models.BooleanField('Perfil publico', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['is_public', '-updated_at']),
            models.Index(fields=['category', '-updated_at']),
        ]

    def __str__(self):
        return f"{self.user} — {self.headline}"


class PortfolioItem(models.Model):
    profile = models.ForeignKey(
        ProfessionalProfile, on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title = models.CharField('Titulo', max_length=150)
    description = models.TextField('Descripcion', max_length=500, blank=True)
    image = models.ImageField(upload_to='professional/portfolio/%Y/%m/')
    url = models.URLField('Enlace al proyecto', blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.profile.user} — {self.title}"


class WorkExperience(models.Model):
    profile = models.ForeignKey(
        ProfessionalProfile, on_delete=models.CASCADE,
        related_name='work_experiences',
    )
    company_name = models.CharField('Empresa', max_length=150)
    position = models.CharField('Cargo', max_length=150)
    description = models.TextField('Descripcion', max_length=1000, blank=True)
    start_date = models.DateField('Fecha inicio')
    end_date = models.DateField('Fecha fin', null=True, blank=True)
    is_current = models.BooleanField('Actualmente', default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.profile.user} — {self.position} en {self.company_name}"
