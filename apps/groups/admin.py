from django.contrib import admin

from .models import (
    Group, GroupMembership, GroupJoinRequest,
    GroupPost, Proposal, ProposalParticipant,
)


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    raw_id_fields = ('user',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'group_type', 'country', 'created_by',
        'is_private', 'is_active', 'created_at',
    )
    list_filter = ('group_type', 'is_private', 'is_active', 'country', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    raw_id_fields = ('created_by',)
    inlines = [GroupMembershipInline]


@admin.register(GroupJoinRequest)
class GroupJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('group__name', 'user__username', 'user__email', 'message')
    raw_id_fields = ('group', 'user')


@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ('group', 'author', 'content_preview', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'created_at')
    search_fields = ('group__name', 'author__username', 'content')
    raw_id_fields = ('group', 'author')

    @admin.display(description='Contenido')
    def content_preview(self, obj):
        return obj.content[:80]


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'proposal_type', 'author', 'group',
        'date', 'is_open', 'created_at',
    )
    list_filter = ('proposal_type', 'is_open', 'created_at')
    search_fields = ('title', 'description', 'author__username', 'group__name')
    raw_id_fields = ('group', 'author')


@admin.register(ProposalParticipant)
class ProposalParticipantAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'user', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('proposal__title', 'user__username', 'user__email')
    raw_id_fields = ('proposal', 'user')
