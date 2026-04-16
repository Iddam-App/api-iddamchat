from django.contrib import admin

from .models import Post, PostImage, Reaction, Comment, SavedPost


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'post_type', 'title', 'is_pinned',
        'is_church_official', 'created_at',
    )
    list_filter = ('post_type', 'is_pinned', 'is_church_official', 'created_at')
    search_fields = ('author__username', 'author__email', 'title', 'content')
    raw_id_fields = ('author',)
    inlines = [PostImageInline]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user', 'post')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content_preview', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'author__email', 'content')
    raw_id_fields = ('post', 'author', 'parent')

    @admin.display(description='Contenido')
    def content_preview(self, obj):
        return obj.content[:80]


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user', 'post')
