from django.contrib import admin

from .models import FriendRequest, Friendship, Follow


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = (
        'from_user__username', 'from_user__email',
        'to_user__username', 'to_user__email',
        'message',
    )
    raw_id_fields = ('from_user', 'to_user')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'user1__username', 'user1__email',
        'user2__username', 'user2__email',
    )
    raw_id_fields = ('user1', 'user2')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'follower__username', 'follower__email',
        'followed__username', 'followed__email',
    )
    raw_id_fields = ('follower', 'followed')
