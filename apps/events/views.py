from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, RSVP
from .serializers import EventSerializer, RSVPSerializer


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    filterset_fields = ['event_type', 'country', 'is_virtual']
    search_fields = ['title', 'description', 'location']

    def get_queryset(self):
        return Event.objects.filter(
            is_active=True, start_date__gte=timezone.now(),
        ).select_related('organizer')

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.select_related('organizer')


class EventRSVPView(APIView):
    def post(self, request, pk):
        event = generics.get_object_or_404(Event, pk=pk, is_active=True)
        rsvp_status = request.data.get('status', 'going')
        rsvp, _ = RSVP.objects.update_or_create(
            event=event, user=request.user,
            defaults={'status': rsvp_status},
        )
        return Response(RSVPSerializer(rsvp, context={'request': request}).data)

    def delete(self, request, pk):
        RSVP.objects.filter(event_id=pk, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventAttendeesView(generics.ListAPIView):
    serializer_class = RSVPSerializer

    def get_queryset(self):
        return RSVP.objects.filter(
            event_id=self.kwargs['pk'],
        ).select_related('user')


class MyEventsView(generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(
            rsvps__user=self.request.user, rsvps__status='going',
            is_active=True,
        ).select_related('organizer')
