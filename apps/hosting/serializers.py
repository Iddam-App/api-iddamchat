from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import HostingMessage, HostingRequest, HostProfile


class HostProfileSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = HostProfile
        fields = [
            'id', 'user', 'is_available', 'max_guests', 'description',
            'address_city', 'address_country', 'amenities', 'rules',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class HostingMessageSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)

    class Meta:
        model = HostingMessage
        fields = ['id', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class HostingRequestSerializer(serializers.ModelSerializer):
    guest = UserMinimalSerializer(read_only=True)
    host = UserMinimalSerializer(read_only=True)
    messages = HostingMessageSerializer(many=True, read_only=True)

    class Meta:
        model = HostingRequest
        fields = [
            'id', 'guest', 'host', 'status', 'message',
            'arrival_date', 'departure_date', 'num_guests',
            'messages', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'guest', 'status', 'created_at', 'updated_at']


class HostingRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostingRequest
        fields = ['host', 'message', 'arrival_date', 'departure_date', 'num_guests']
