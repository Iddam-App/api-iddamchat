from django.contrib import admin

from .models import HostProfile, HostingRequest, HostingMessage


@admin.register(HostProfile)
class HostProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'address_city', 'address_country', 'is_available',
        'max_guests', 'created_at',
    )
    list_filter = ('is_available', 'address_country', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'address_city',
        'description', 'amenities',
    )
    raw_id_fields = ('user',)


@admin.register(HostingRequest)
class HostingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'guest', 'host', 'status', 'arrival_date',
        'departure_date', 'num_guests', 'created_at',
    )
    list_filter = ('status', 'arrival_date', 'created_at')
    search_fields = (
        'guest__username', 'guest__email',
        'host__username', 'host__email',
        'message',
    )
    raw_id_fields = ('guest', 'host')


@admin.register(HostingMessage)
class HostingMessageAdmin(admin.ModelAdmin):
    list_display = ('request', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'sender__email', 'content')
    raw_id_fields = ('request', 'sender')

    @admin.display(description='Contenido')
    def content_preview(self, obj):
        return obj.content[:80]
