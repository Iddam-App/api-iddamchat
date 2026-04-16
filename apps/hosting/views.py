from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HostingMessage, HostingRequest, HostProfile
from .serializers import (
    HostingMessageSerializer, HostingRequestCreateSerializer,
    HostingRequestSerializer, HostProfileSerializer,
)


class HostProfileListView(generics.ListAPIView):
    serializer_class = HostProfileSerializer
    filterset_fields = ['address_country', 'address_city', 'is_available']
    search_fields = ['address_city', 'description', 'user__congregation']

    def get_queryset(self):
        return HostProfile.objects.filter(
            is_available=True,
        ).select_related('user')


class MyHostProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = HostProfileSerializer

    def get_object(self):
        obj, _ = HostProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'address_city': self.request.user.city,
                'address_country': self.request.user.country,
            },
        )
        return obj


class HostingRequestCreateView(generics.CreateAPIView):
    serializer_class = HostingRequestCreateSerializer

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)


class MyHostingRequestsView(generics.ListAPIView):
    serializer_class = HostingRequestSerializer

    def get_queryset(self):
        return HostingRequest.objects.filter(
            guest=self.request.user,
        ).select_related('guest', 'host').prefetch_related('messages__sender')


class ReceivedHostingRequestsView(generics.ListAPIView):
    serializer_class = HostingRequestSerializer

    def get_queryset(self):
        return HostingRequest.objects.filter(
            host=self.request.user,
        ).select_related('guest', 'host').prefetch_related('messages__sender')


class RespondHostingRequestView(APIView):
    def post(self, request, pk, action):
        hr = generics.get_object_or_404(
            HostingRequest, pk=pk, host=request.user, status='pending',
        )
        if action in ('accepted', 'rejected'):
            hr.status = action
            hr.save(update_fields=['status', 'updated_at'])
        return Response(
            HostingRequestSerializer(hr, context={'request': request}).data,
        )


class HostingMessageCreateView(APIView):
    def post(self, request, pk):
        hr = generics.get_object_or_404(HostingRequest, pk=pk)
        if request.user not in (hr.guest, hr.host):
            return Response(
                {'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN,
            )
        msg = HostingMessage.objects.create(
            request=hr, sender=request.user,
            content=request.data.get('content', ''),
        )
        return Response(
            HostingMessageSerializer(msg, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
