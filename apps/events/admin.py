from django.contrib import admin

from .models import Event, RSVP


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'event_type', 'organizer', 'group', 'country',
        'start_date', 'is_virtual', 'is_active', 'created_at',
    )
    list_filter = (
        'event_type', 'is_virtual', 'is_active', 'country',
        'start_date', 'created_at',
    )
    search_fields = (
        'title', 'description', 'location',
        'organizer__username', 'organizer__email',
        'group__name',
    )
    raw_id_fields = ('organizer', 'group')


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('event__title', 'user__username', 'user__email')
    raw_id_fields = ('event', 'user')
