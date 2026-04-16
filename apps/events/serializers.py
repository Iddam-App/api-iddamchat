from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import Event, RSVP


class RSVPSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'user', 'status', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    organizer = UserMinimalSerializer(read_only=True)
    attendee_count = serializers.ReadOnlyField()
    my_rsvp = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'group', 'event_type', 'title',
            'description', 'cover_image', 'location', 'country',
            'start_date', 'end_date', 'is_virtual', 'meeting_link',
            'max_attendees', 'is_active', 'attendee_count',
            'my_rsvp', 'created_at',
        ]
        read_only_fields = ['id', 'organizer', 'created_at']

    def get_my_rsvp(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rsvp = obj.rsvps.filter(user=request.user).first()
            if rsvp:
                return rsvp.status
        return None
