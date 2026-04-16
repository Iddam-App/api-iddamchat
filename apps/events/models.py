from django.conf import settings
from django.db import models


class Event(models.Model):
    EVENT_TYPES = [
        ('youth_meeting', 'Reunión de Jóvenes'),
        ('fasting', 'Día de Ayuno'),
        ('musical', 'Evento Musical'),
        ('study', 'Estudio Bíblico'),
        ('service', 'Servicio'),
        ('camp', 'Campamento'),
        ('social', 'Actividad Social'),
        ('other', 'Otro'),
    ]

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='organized_events',
    )
    group = models.ForeignKey(
        'groups.Group', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='events',
    )
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='events/covers/%Y/%m/', blank=True)
    location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=5, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['event_type', 'start_date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    @property
    def attendee_count(self):
        return self.rsvps.filter(status='going').count()


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('going', 'Asistiré'),
        ('maybe', 'Tal vez'),
        ('not_going', 'No asistiré'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='event_rsvps',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='going')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} → {self.event} ({self.status})"
