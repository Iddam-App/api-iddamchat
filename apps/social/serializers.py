from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import Follow, FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserMinimalSerializer(read_only=True)
    to_user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'message', 'created_at']
        read_only_fields = ['id', 'from_user', 'status', 'created_at']


class FriendRequestCreateSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField()
    message = serializers.CharField(max_length=255, required=False, default='')

    def validate_to_user_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Usuario no encontrado.')
        if value == self.context['request'].user.pk:
            raise serializers.ValidationError('No puedes enviarte solicitud a ti mismo.')
        return value


class FriendshipSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['id', 'friend', 'created_at']

    def get_friend(self, obj):
        request = self.context['request']
        friend = obj.user2 if obj.user1 == request.user else obj.user1
        return UserMinimalSerializer(friend, context=self.context).data


class FollowSerializer(serializers.ModelSerializer):
    follower = UserMinimalSerializer(read_only=True)
    followed = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
