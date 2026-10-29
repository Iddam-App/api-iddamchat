from django.contrib import admin

from .models import (
    CareerTip, JobBookmark, JobCategory, JobPosting,
    TipCategory, TipLike,
)


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    list_editable = ('order',)
    search_fields = ('name',)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'company_name', 'category',
        'job_type', 'modality', 'is_active', 'created_at',
    )
    list_filter = ('is_active', 'job_type', 'modality', 'experience_level', 'category', 'created_at')
    search_fields = ('title', 'description', 'company_name', 'author__username')
    raw_id_fields = ('author', 'category')


@admin.register(JobBookmark)
class JobBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    raw_id_fields = ('user', 'job')


@admin.register(TipCategory)
class TipCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')
    list_filter = ('parent',)
    list_editable = ('order',)
    search_fields = ('name',)


@admin.register(CareerTip)
class CareerTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'likes_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('author', 'category')


@admin.register(TipLike)
class TipLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tip', 'created_at')
    raw_id_fields = ('user', 'tip')
