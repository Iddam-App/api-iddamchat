from django.db.models import F, Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services import create_notification

from .models import (
    CareerTip, JobBookmark, JobCategory, JobPosting,
    TipCategory, TipLike,
)
from .serializers import (
    CareerTipCreateSerializer, CareerTipDetailSerializer,
    CareerTipListSerializer, JobCategorySerializer,
    JobPostingCreateSerializer, JobPostingDetailSerializer,
    JobPostingListSerializer, TipCategorySerializer,
)


# ─── Job Categories ──────────────────────────────────────────────

class JobCategoryListView(generics.ListAPIView):
    serializer_class = JobCategorySerializer
    queryset = JobCategory.objects.all()
    pagination_class = None


# ─── Job Postings ────────────────────────────────────────────────

class JobPostingListView(generics.ListAPIView):
    serializer_class = JobPostingListSerializer

    def get_queryset(self):
        qs = JobPosting.objects.filter(
            is_active=True,
        ).select_related('author', 'category')

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        job_type = self.request.query_params.get('job_type')
        if job_type:
            qs = qs.filter(job_type=job_type)

        modality = self.request.query_params.get('modality')
        if modality:
            qs = qs.filter(modality=modality)

        experience_level = self.request.query_params.get('experience_level')
        if experience_level:
            qs = qs.filter(experience_level=experience_level)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(company_name__icontains=search)
                | Q(skills__icontains=search)
            )

        return qs


class JobPostingCreateView(generics.CreateAPIView):
    serializer_class = JobPostingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class JobPostingDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = JobPostingDetailSerializer

    def get_queryset(self):
        return JobPosting.objects.select_related('author', 'category')

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo el autor puede editar esta oferta.')
        serializer.save()


class JobPostingDeleteView(APIView):
    def post(self, request, pk):
        try:
            job = JobPosting.objects.get(pk=pk, author=request.user)
        except JobPosting.DoesNotExist:
            return Response(
                {'detail': 'No encontrado o no autorizado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        job.is_active = False
        job.save(update_fields=['is_active', 'updated_at'])
        return Response({'detail': 'Oferta desactivada.'})


# ─── Bookmarks ───────────────────────────────────────────────────

class ToggleBookmarkView(APIView):
    def post(self, request, pk):
        try:
            job = JobPosting.objects.get(pk=pk, is_active=True)
        except JobPosting.DoesNotExist:
            return Response(
                {'detail': 'Oferta no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        bookmark, created = JobBookmark.objects.get_or_create(
            user=request.user, job=job,
        )
        if not created:
            bookmark.delete()
            return Response({'bookmarked': False})
        return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)


class MyJobPostingsView(generics.ListAPIView):
    serializer_class = JobPostingListSerializer

    def get_queryset(self):
        return JobPosting.objects.filter(
            author=self.request.user,
        ).select_related('author', 'category')


class MyBookmarksView(generics.ListAPIView):
    serializer_class = JobPostingListSerializer

    def get_queryset(self):
        return JobPosting.objects.filter(
            bookmarks__user=self.request.user,
            is_active=True,
        ).select_related('author', 'category')


# ─── Tip Categories ──────────────────────────────────────────────

class TipCategoryListView(generics.ListAPIView):
    serializer_class = TipCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return TipCategory.objects.filter(parent__isnull=True).prefetch_related('children')


# ─── Career Tips ─────────────────────────────────────────────────

class CareerTipListView(generics.ListAPIView):
    serializer_class = CareerTipListSerializer

    def get_queryset(self):
        qs = CareerTip.objects.select_related('author', 'category', 'category__parent')

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(
                Q(category_id=category) | Q(category__parent_id=category)
            )

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        return qs


class CareerTipCreateView(generics.CreateAPIView):
    serializer_class = CareerTipCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CareerTipDetailView(generics.RetrieveAPIView):
    serializer_class = CareerTipDetailSerializer

    def get_queryset(self):
        return CareerTip.objects.select_related('author', 'category', 'category__parent')


class ToggleTipLikeView(APIView):
    def post(self, request, pk):
        try:
            tip = CareerTip.objects.select_related('author').get(pk=pk)
        except CareerTip.DoesNotExist:
            return Response(
                {'detail': 'Consejo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        like, created = TipLike.objects.get_or_create(
            user=request.user, tip=tip,
        )
        if created:
            CareerTip.objects.filter(pk=pk).update(likes_count=F('likes_count') + 1)
            tip.refresh_from_db()
            create_notification(
                recipient=tip.author,
                sender=request.user,
                notification_type='tip_like',
                message=f'Le dio like a tu consejo "{tip.title[:60]}"',
                content_type='career_tip',
                content_id=tip.id,
            )
            return Response(
                {'liked': True, 'likes_count': tip.likes_count},
                status=status.HTTP_201_CREATED,
            )
        else:
            like.delete()
            CareerTip.objects.filter(pk=pk).update(likes_count=F('likes_count') - 1)
            tip.refresh_from_db()
            return Response({'liked': False, 'likes_count': tip.likes_count})
