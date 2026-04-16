from django.contrib import admin
from django.utils.html import format_html

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'original_content', 'was_filtered',
                       'matched_words', 'is_read', 'created_at')
    fields = ('sender', 'content', 'original_content', 'was_filtered',
              'is_read', 'created_at')
    ordering = ('-created_at',)
    max_num = 50


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'message_count', 'last_activity', 'created_at')
    search_fields = (
        'user1__username', 'user1__email', 'user1__first_name',
        'user2__username', 'user2__email', 'user2__first_name',
    )
    raw_id_fields = ('user1', 'user2')
    inlines = [MessageInline]

    @admin.display(description='Mensajes')
    def message_count(self, obj):
        count = obj.messages.count()
        flagged = obj.messages.filter(was_filtered=True).count()
        if flagged:
            return format_html(
                '{} (<span style="color:red">{} censurados</span>)',
                count, flagged,
            )
        return count

    @admin.display(description='Última Actividad')
    def last_activity(self, obj):
        return obj.updated_at


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'conversation', 'sender', 'content_preview',
        'filter_status', 'is_read', 'created_at',
    )
    list_filter = ('was_filtered', 'is_read', 'created_at')
    search_fields = (
        'content', 'original_content', 'matched_words',
        'sender__username', 'sender__email',
    )
    raw_id_fields = ('conversation', 'sender')
    readonly_fields = ('original_content', 'was_filtered', 'matched_words')

    @admin.display(description='Contenido')
    def content_preview(self, obj):
        return obj.content[:100]

    @admin.display(description='Filtro')
    def filter_status(self, obj):
        if obj.was_filtered:
            return format_html(
                '<span style="color:red" title="Original: {}">CENSURADO</span>',
                obj.original_content[:200],
            )
        return format_html('<span style="color:green">OK</span>')
