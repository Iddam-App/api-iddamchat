from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, FileResponse, Http404
from django.urls import include, path

from apps.core.views_web import (
    landing_view, login_view, register_view,
    feed_view, hobbies_view, hosting_view, chat_view, groups_view,
    profile_view, edit_profile_view, post_detail_view,
    notifications_view, explore_view, events_view,
)


# ─── PWA helpers (serve from root scope) ─────────────────────────
def sw_js(request):
    """Serve service worker from root scope for PWA install."""
    sw_path = settings.BASE_DIR / 'static' / 'js' / 'sw.js'
    return HttpResponse(sw_path.read_text(), content_type='application/javascript')


def manifest_json(request):
    """Serve manifest from root scope with correct MIME type."""
    manifest_path = settings.BASE_DIR / 'static' / 'manifest.json'
    return HttpResponse(manifest_path.read_text(), content_type='application/manifest+json')


def pwa_icon(request, filename):
    """Serve PWA icons directly (bypass WhiteNoise hashing)."""
    icon_path = settings.BASE_DIR / 'static' / 'img' / 'icons' / filename
    if icon_path.exists():
        content_type = 'image/png'
        if filename.endswith('.ico'):
            content_type = 'image/x-icon'
        elif filename.endswith('.svg'):
            content_type = 'image/svg+xml'
        return FileResponse(open(icon_path, 'rb'), content_type=content_type)
    raise Http404


urlpatterns = [
    # PWA files (must be at root scope)
    path('sw.js', sw_js, name='service_worker'),
    path('manifest.json', manifest_json, name='manifest'),
    path('icons/<str:filename>', pwa_icon, name='pwa_icon'),

    # Web pages
    path('', landing_view, name='landing'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('feed/', feed_view, name='feed'),
    path('hobbies/', hobbies_view, name='hobbies'),
    path('hosting/', hosting_view, name='hosting'),
    path('chat/', chat_view, name='chat'),
    path('chat/<int:user_id>/', chat_view, name='chat_with_user'),
    path('groups/', groups_view, name='groups'),
    path('profile/', profile_view, name='my_profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('profile/<int:user_id>/', profile_view, name='user_profile'),
    path('post/<int:pk>/', post_detail_view, name='post_detail'),
    path('notifications/', notifications_view, name='notifications'),
    path('explore/', explore_view, name='explore'),
    path('events/', events_view, name='events'),

    path('admin/', admin.site.urls),

    # API v1
    path('api/auth/', include('apps.core.urls', namespace='core')),
    path('api/profiles/', include('apps.profiles.urls', namespace='profiles')),
    path('api/social/', include('apps.social.urls', namespace='social')),
    path('api/posts/', include('apps.posts.urls', namespace='posts')),
    path('api/groups/', include('apps.groups.urls', namespace='groups')),
    path('api/hosting/', include('apps.hosting.urls', namespace='hosting')),
    path('api/events/', include('apps.events.urls', namespace='events')),
    path('api/bible/', include('apps.bible.urls', namespace='bible')),
    path('api/notes/', include('apps.notes.urls', namespace='notes')),
    path('api/content/', include('apps.content.urls', namespace='content')),
    path('api/chat/', include('apps.chat.urls', namespace='chat')),
    path('api/moderation/', include('apps.moderation.urls', namespace='moderation')),
    path('api/notifications/', include('apps.notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
