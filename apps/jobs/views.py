from django.db.models import Count, F, Q, Subquery, OuterRef
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import UserLanguage
from apps.notifications.services import create_notification

from .models import (
    CareerTip, JobBookmark, JobCategory, JobPosting,
    PortfolioItem, ProfessionalProfile, TipCategory, TipLike,
    WorkExperience,
)
from .serializers import (
    CareerTipCreateSerializer, CareerTipDetailSerializer,
    CareerTipListSerializer, JobCategorySerializer,
    JobPostingCreateSerializer, JobPostingDetailSerializer,
    JobPostingListSerializer, PortfolioItemSerializer,
    ProfessionalProfileCreateUpdateSerializer,
    ProfessionalProfileDetailSerializer,
    ProfessionalProfileListSerializer, TipCategorySerializer,
    WorkExperienceSerializer,
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


# ─── Professional Profiles ───────────────────────────────────────

class ProfessionalProfileListView(generics.ListAPIView):
    serializer_class = ProfessionalProfileListSerializer

    def get_queryset(self):
        qs = ProfessionalProfile.objects.filter(
            is_public=True,
        ).select_related('user', 'category')

        # Annotate shared languages count with current user
        user = self.request.user
        if user.is_authenticated:
            my_langs = UserLanguage.objects.filter(
                user=user,
            ).values_list('language_code', flat=True)
            shared = UserLanguage.objects.filter(
                user=OuterRef('user'),
                language_code__in=list(my_langs),
            ).values('user').annotate(cnt=Count('id')).values('cnt')
            qs = qs.annotate(
                shared_languages_count=Subquery(shared),
            ).order_by('-shared_languages_count', '-updated_at')
        else:
            qs = qs.order_by('-updated_at')

        # Filters
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        country = self.request.query_params.get('country')
        if country:
            qs = qs.filter(user__country=country)

        language = self.request.query_params.get('language')
        if language:
            qs = qs.filter(user__languages__language_code=language).distinct()

        availability = self.request.query_params.get('availability')
        if availability:
            qs = qs.filter(availability=availability)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(headline__icontains=search)
                | Q(skills__icontains=search)
                | Q(services__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )

        return qs


class ProfessionalProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfessionalProfileDetailSerializer
    lookup_field = 'user_id'

    def get_queryset(self):
        return ProfessionalProfile.objects.filter(
            is_public=True,
        ).select_related('user', 'category').prefetch_related(
            'portfolio_items', 'work_experiences',
        )


class MyProfessionalProfileView(generics.RetrieveUpdateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProfessionalProfileCreateUpdateSerializer
        return ProfessionalProfileDetailSerializer

    def get_object(self):
        obj, _ = ProfessionalProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'headline': ''},
        )
        return obj


class PortfolioItemCreateView(generics.CreateAPIView):
    serializer_class = PortfolioItemSerializer

    def perform_create(self, serializer):
        profile, _ = ProfessionalProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'headline': ''},
        )
        serializer.save(profile=profile)


class PortfolioItemDeleteView(APIView):
    def delete(self, request, pk):
        try:
            item = PortfolioItem.objects.get(
                pk=pk, profile__user=request.user,
            )
        except PortfolioItem.DoesNotExist:
            return Response(
                {'detail': 'No encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkExperienceCreateView(generics.CreateAPIView):
    serializer_class = WorkExperienceSerializer

    def perform_create(self, serializer):
        profile, _ = ProfessionalProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'headline': ''},
        )
        serializer.save(profile=profile)


class WorkExperienceUpdateDeleteView(APIView):
    def put(self, request, pk):
        try:
            exp = WorkExperience.objects.get(
                pk=pk, profile__user=request.user,
            )
        except WorkExperience.DoesNotExist:
            return Response(
                {'detail': 'No encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WorkExperienceSerializer(exp, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            exp = WorkExperience.objects.get(
                pk=pk, profile__user=request.user,
            )
        except WorkExperience.DoesNotExist:
            return Response(
                {'detail': 'No encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        exp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
