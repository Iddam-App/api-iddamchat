from django.conf import settings
from django.db import models


class HostProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='host_profile',
    )
    is_available = models.BooleanField(default=True)
    max_guests = models.PositiveSmallIntegerField('Capacidad', default=1)
    description = models.TextField('Descripción del hospedaje', blank=True)
    address_city = models.CharField('Ciudad', max_length=100)
    address_country = models.CharField('País', max_length=5)
    amenities = models.TextField('Comodidades', blank=True)
    rules = models.TextField('Reglas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['address_country', 'address_city']

    def __str__(self):
        return f"Hospedaje de {self.user} en {self.address_city}"


class HostingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ]

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='hosting_requests_sent',
    )
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='hosting_requests_received',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField('Mensaje')
    arrival_date = models.DateField('Fecha de llegada')
    departure_date = models.DateField('Fecha de salida')
    num_guests = models.PositiveSmallIntegerField('Número de huéspedes', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.guest} → {self.host} ({self.arrival_date})"


class HostingMessage(models.Model):
    request = models.ForeignKey(
        HostingRequest, on_delete=models.CASCADE, related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
