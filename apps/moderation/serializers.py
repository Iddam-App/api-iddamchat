from rest_framework import serializers

from .models import ContentFlag, ImageReview


class ReportContentSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(
        choices=['post', 'comment', 'message', 'story', 'group_post', 'profile'],
    )
    content_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)


class ContentFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentFlag
        fields = [
            'id', 'flag_type', 'content_type', 'content_id',
            'flagged_user', 'matched_words', 'original_content',
            'reason', 'status', 'created_at',
        ]
