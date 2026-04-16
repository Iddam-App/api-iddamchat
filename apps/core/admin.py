from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'email', 'full_name_display', 'nickname', 'country',
        'congregation', 'is_active', 'is_staff', 'warnings_count',
        'bans_count', 'last_login', 'created_at',
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_host_available',
        'country', 'created_at',
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 'nickname',
        'congregation', 'city', 'phone', 'instagram',
    )
    ordering = ('-created_at',)
    list_per_page = 50

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
            'description': (
                'La contraseña se guarda encriptada por seguridad. '
                'Usa el enlace "Cambiar contraseña" abajo para establecer una nueva.'
            ),
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'nickname', 'age',
            ),
        }),
        ('Perfil IDDAM', {
            'fields': (
                'avatar', 'country', 'city', 'congregation',
                'instagram', 'phone', 'bio', 'is_host_available',
            ),
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
        ('Fechas', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Perfil IDDAM', {
            'fields': (
                'first_name', 'last_name', 'nickname',
                'country', 'congregation',
            ),
        }),
    )

    @admin.display(description='Nombre')
    def full_name_display(self, obj):
        name = obj.get_full_name()
        if not obj.is_active:
            return format_html('<span style="color:red;text-decoration:line-through">{}</span>', name)
        return name

    @admin.display(description='Advertencias')
    def warnings_count(self, obj):
        count = obj.warnings.count()
        if count > 0:
            return format_html('<span style="color:orange;font-weight:bold">{}</span>', count)
        return 0

    @admin.display(description='Bans')
    def bans_count(self, obj):
        count = obj.bans.filter(is_active=True).count()
        if count > 0:
            return format_html('<span style="color:red;font-weight:bold">{}</span>', count)
        return 0

    actions = ['activate_users', 'deactivate_users', 'reset_password']

    @admin.action(description='Activar usuarios seleccionados')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} usuarios activados.')

    @admin.action(description='Desactivar usuarios seleccionados')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} usuarios desactivados.')

    @admin.action(description='Resetear contraseña a "iddam2026"')
    def reset_password(self, request, queryset):
        for user in queryset:
            user.set_password('iddam2026')
            user.save(update_fields=['password'])
        self.message_user(
            request,
            f'Contraseña reseteada para {queryset.count()} usuario(s) a "iddam2026". '
            'Deben cambiarla al iniciar sesión.',
        )
