from django.http import JsonResponse
from django.utils import timezone


class BanCheckMiddleware:
    """Bloquea requests de usuarios baneados."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            from apps.moderation.models import UserBan
            active_ban = UserBan.objects.filter(
                user=request.user,
                is_active=True,
            ).first()

            if active_ban:
                # Verificar si el ban temporal expiró
                if not active_ban.is_permanent and active_ban.expires_at:
                    if active_ban.expires_at <= timezone.now():
                        active_ban.is_active = False
                        active_ban.save(update_fields=['is_active'])
                        return self.get_response(request)

                return JsonResponse({
                    'detail': 'Tu cuenta ha sido suspendida.',
                    'reason': active_ban.reason,
                    'is_permanent': active_ban.is_permanent,
                    'expires_at': active_ban.expires_at.isoformat() if active_ban.expires_at else None,
                }, status=403)

        return self.get_response(request)
