from django.contrib.auth.models import AbstractUser
from django.db import models

COUNTRY_CHOICES = [
    ('AR', 'Argentina'), ('BO', 'Bolivia'), ('BR', 'Brasil'),
    ('CL', 'Chile'), ('CO', 'Colombia'), ('CR', 'Costa Rica'),
    ('CU', 'Cuba'), ('EC', 'Ecuador'), ('SV', 'El Salvador'),
    ('GT', 'Guatemala'), ('HN', 'Honduras'), ('MX', 'México'),
    ('NI', 'Nicaragua'), ('PA', 'Panamá'), ('PY', 'Paraguay'),
    ('PE', 'Perú'), ('PR', 'Puerto Rico'), ('DO', 'Rep. Dominicana'),
    ('UY', 'Uruguay'), ('VE', 'Venezuela'), ('US', 'Estados Unidos'),
    ('ES', 'España'), ('OTHER', 'Otro'),
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True)
    nickname = models.CharField('Apodo', max_length=50, blank=True)
    age = models.PositiveSmallIntegerField('Edad', null=True, blank=True)
    country = models.CharField('País', max_length=5, choices=COUNTRY_CHOICES, blank=True)
    city = models.CharField('Ciudad', max_length=100, blank=True)

    # Social links
    instagram = models.CharField('Instagram', max_length=100, blank=True)
    phone = models.CharField('Teléfono', max_length=30, blank=True)
    bio = models.TextField('Descripción', max_length=500, blank=True)

    # Church info
    congregation = models.CharField('Congregación', max_length=150, blank=True)
    is_host_available = models.BooleanField('Disponible como hospedaje', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def display_name(self):
        if self.nickname:
            return f"{self.first_name} ({self.nickname})"
        return self.get_full_name()
