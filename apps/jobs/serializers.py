from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import (
    CareerTip, JobBookmark, JobCategory, JobPosting,
    TipCategory, TipLike,
)


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'icon', 'order']


class JobPostingListSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            'id', 'author', 'title', 'description', 'category', 'category_name',
            'company_name', 'job_type', 'modality', 'experience_level',
            'location_city', 'location_country', 'skills',
            'salary_type', 'salary_min', 'salary_max', 'salary_currency',
            'contact_email', 'contact_phone', 'contact_url',
            'image', 'is_active', 'application_deadline',
            'is_bookmarked', 'created_at',
        ]

    def get_is_bookmarked(self, obj):
        user = self.context.get('request', None)
        if user and hasattr(user, 'user'):
            user = user.user
        else:
            return False
        if not user or not user.is_authenticated:
            return False
        if not hasattr(self, '_bookmark_set'):
            self._bookmark_set = set(
                JobBookmark.objects.filter(user=user)
                .values_list('job_id', flat=True)
            )
        return obj.id in self._bookmark_set


class JobPostingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'category', 'company_name',
            'job_type', 'modality', 'experience_level',
            'location_city', 'location_country', 'skills', 'requirements',
            'salary_type', 'salary_min', 'salary_max', 'salary_currency',
            'contact_email', 'contact_phone', 'contact_url',
            'image', 'application_deadline',
        ]
        read_only_fields = ['id']


class JobPostingDetailSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            'id', 'author', 'title', 'description', 'category', 'category_name',
            'company_name', 'job_type', 'modality', 'experience_level',
            'location_city', 'location_country', 'skills', 'requirements',
            'salary_type', 'salary_min', 'salary_max', 'salary_currency',
            'contact_email', 'contact_phone', 'contact_url',
            'image', 'is_active', 'application_deadline',
            'is_bookmarked', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobBookmark.objects.filter(user=request.user, job=obj).exists()
        return False


class TipCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = TipCategory
        fields = ['id', 'name', 'order', 'parent', 'children']

    def get_children(self, obj):
        if obj.parent is None:
            return TipCategorySerializer(obj.children.all(), many=True).data
        return []


class CareerTipListSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    category_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CareerTip
        fields = [
            'id', 'author', 'category', 'category_name',
            'title', 'content', 'image', 'likes_count',
            'is_liked', 'created_at',
        ]

    def get_category_name(self, obj):
        if obj.category:
            return str(obj.category)
        return ''

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not hasattr(self, '_like_set'):
                self._like_set = set(
                    TipLike.objects.filter(user=request.user)
                    .values_list('tip_id', flat=True)
                )
            return obj.id in self._like_set
        return False


class CareerTipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerTip
        fields = ['id', 'title', 'content', 'category', 'image']
        read_only_fields = ['id']


class CareerTipDetailSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    category_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CareerTip
        fields = [
            'id', 'author', 'category', 'category_name',
            'title', 'content', 'image', 'likes_count',
            'is_liked', 'created_at', 'updated_at',
        ]

    def get_category_name(self, obj):
        if obj.category:
            return str(obj.category)
        return ''

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TipLike.objects.filter(user=request.user, tip=obj).exists()
        return False
