from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import BannedWord, ContentFlag, ImageReview, UserBan, UserWarning


@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'severity', 'is_active', 'created_at')
    list_filter = ('category', 'severity', 'is_active')
    search_fields = ('word',)
    list_editable = ('category', 'severity', 'is_active')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Invalida cache al cambiar palabras
        from .filter import invalidate_cache
        invalidate_cache()


@admin.register(ContentFlag)
class ContentFlagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'flag_type', 'content_type', 'flagged_user',
        'matched_words_short', 'severity_badge', 'status', 'created_at',
    )
    list_filter = ('flag_type', 'content_type', 'status', 'created_at')
    search_fields = (
        'flagged_user__username', 'flagged_user__email',
        'matched_words', 'original_content', 'reason',
    )
    raw_id_fields = ('flagged_user', 'reported_by', 'reviewed_by')
    readonly_fields = ('original_content', 'matched_words', 'created_at')
    list_per_page = 50
    actions = ['mark_reviewed', 'mark_dismissed', 'mark_action_taken']

    @admin.display(description='Palabras')
    def matched_words_short(self, obj):
        return obj.matched_words[:80] if obj.matched_words else '-'

    @admin.display(description='Severidad')
    def severity_badge(self, obj):
        if 'grooming' in obj.matched_words.lower():
            return format_html('<span style="color:red;font-weight:bold">GROOMING</span>')
        if obj.flag_type == 'user_report':
            return format_html('<span style="color:orange">Reporte</span>')
        return format_html('<span style="color:#2EA3F2">Auto</span>')

    @admin.action(description='Marcar como Revisado')
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed', reviewed_by=request.user, reviewed_at=timezone.now())

    @admin.action(description='Descartar')
    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed', reviewed_by=request.user, reviewed_at=timezone.now())

    @admin.action(description='Acción Tomada')
    def mark_action_taken(self, request, queryset):
        queryset.update(status='action_taken', reviewed_by=request.user, reviewed_at=timezone.now())


@admin.register(ImageReview)
class ImageReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'preview_image', 'status', 'created_at')
    list_filter = ('status', 'content_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user', 'reviewed_by')
    actions = ['approve_images', 'reject_images']

    @admin.display(description='Vista Previa')
    def preview_image(self, obj):
        return format_html(
            '<a href="{}" target="_blank">'
            '<img src="{}" style="max-height:60px;max-width:100px"/></a>',
            obj.image_url, obj.image_url,
        )

    @admin.action(description='Aprobar Imágenes')
    def approve_images(self, request, queryset):
        queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())

    @admin.action(description='Rechazar Imágenes')
    def reject_images(self, request, queryset):
        queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())


@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason_short', 'issued_by', 'related_flag', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'reason')
    raw_id_fields = ('user', 'issued_by', 'related_flag')

    @admin.display(description='Razón')
    def reason_short(self, obj):
        return obj.reason[:80]


@admin.register(UserBan)
class UserBanAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'reason_short', 'banned_by',
        'is_permanent', 'expires_at', 'is_active', 'created_at',
    )
    list_filter = ('is_permanent', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'reason')
    raw_id_fields = ('user', 'banned_by')
    list_editable = ('is_active',)

    @admin.display(description='Razón')
    def reason_short(self, obj):
        return obj.reason[:80]
