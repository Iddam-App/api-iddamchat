from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import (
    Group, GroupJoinRequest, GroupMembership, GroupPost,
    Proposal, ProposalParticipant,
)


class GroupSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'group_type', 'description', 'avatar', 'cover',
            'country', 'created_by', 'is_private', 'member_count',
            'is_member', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.memberships.filter(user=request.user, is_active=True).exists()
        return False


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'role', 'joined_at']


class GroupJoinRequestSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = GroupJoinRequest
        fields = ['id', 'user', 'status', 'message', 'created_at']


class GroupPostSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)

    class Meta:
        model = GroupPost
        fields = ['id', 'group', 'author', 'content', 'image',
                  'is_pinned', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class ProposalSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()
    is_participating = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            'id', 'group', 'author', 'proposal_type', 'title',
            'description', 'date', 'is_open', 'participant_count',
            'is_participating', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']

    def get_participant_count(self, obj):
        return obj.participants.count()

    def get_is_participating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(user=request.user).exists()
        return False
