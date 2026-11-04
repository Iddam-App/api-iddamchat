from django.contrib import admin

from .models import (
    CareerTip, JobBookmark, JobCategory, JobPosting,
    PortfolioItem, ProfessionalProfile, TipCategory, TipLike,
    WorkExperience,
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


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 0


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'category', 'availability', 'is_public', 'updated_at')
    list_filter = ('availability', 'is_public', 'category')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'headline', 'skills')
    raw_id_fields = ('user', 'category')
    inlines = [PortfolioItemInline, WorkExperienceInline]


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'order', 'created_at')
    raw_id_fields = ('profile',)


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company_name', 'profile', 'start_date', 'end_date', 'is_current')
    raw_id_fields = ('profile',)
