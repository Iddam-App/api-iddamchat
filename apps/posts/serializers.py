from rest_framework import serializers

from apps.core.serializers import UserMinimalSerializer

from .models import Comment, Post, PostImage, Reaction, SavedPost


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'order']


class ReactionSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'parent', 'content', 'created_at',
                  'updated_at', 'replies']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.select_related('author').all()[:5]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    reaction_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    my_reaction = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'post_type', 'title', 'content',
            'images', 'is_pinned', 'is_church_official', 'is_hidden',
            'reaction_count', 'comment_count', 'my_reaction',
            'is_saved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'is_church_official', 'created_at', 'updated_at']

    def get_my_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True,
    )

    class Meta:
        model = Post
        fields = ['post_type', 'title', 'content', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        post = Post.objects.create(**validated_data)
        for i, img in enumerate(images):
            PostImage.objects.create(post=post, image=img, order=i)
        return post
