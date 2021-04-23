from rest_framework import serializers
from .models import Post, Comment, Rating
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Q


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for object author info"""

    class Meta:
        model = get_user_model()
        fields = ('username', 'profile_pic')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the comment objects"""
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'posted_on')
        read_only_fields = ('author', 'id', 'posted_on')


class PostSerializer(serializers.ModelSerializer):
    """Serializer for the post objects"""
    author = AuthorSerializer(read_only=True)
    photo = serializers.ImageField(max_length=None, allow_empty_file=False)
    number_of_comments = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField('paginated_post_ratings')
    post_comments = serializers.SerializerMethodField(
        'paginated_post_comments')
    liked_by_req_user = serializers.SerializerMethodField()
    favorited_by_req_user = serializers.SerializerMethodField()
    rated_by_req_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author',  'photo',
                  'text', 'location', 'posted_on',
                  'number_of_likes', 'number_of_comments',
                  'post_comments', 'average_rating', 'rating', 'liked_by_req_user', 'favorited_by_req_user', 'rated_by_req_user', )
        ordering = [id, ]


    def get_number_of_comments(self, obj):
        return Comment.objects.filter(post=obj).count()


    def get_average_rating(self, obj):
        rating = obj.post_ratings.all().aggregate(Avg('rating')).get('rating__avg')
        return rating

    def paginated_post_ratings(self, obj):
        page_size = 10
        paginator = Paginator(obj.post_ratings.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1

        post_ratings = paginator.page(page)
        serializer = RatingSerializer(post_ratings, many=True)

        return serializer.data

    def paginated_post_comments(self, obj):
        page_size = 5
        paginator = Paginator(obj.post_comments.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1

        post_comments = paginator.page(page)
        serializer = CommentSerializer(post_comments, many=True)

        return serializer.data

    def get_liked_by_req_user(self, obj):
        user = self.context['request'].user
        return user in obj.likes.all()

    def get_favorited_by_req_user(self, obj):
        user = self.context['request'].user
        return user in obj.favorites.all()

    def get_rated_by_req_user(self, obj):
        user = self.context['request'].user
        rating = Rating.objects.filter(post=obj, user=user)
        if rating:
            return True
        else:
            return False


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('user', 'rating')
        read_only_fields = ('user', )
        ordering = ['-rating', ]

    def validate_user(self, obj):
        user = self.context['request'].user
        if user in obj.ratings:
            raise serializers.ValidationError('You have already rated the post')
        return obj

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating > 5:
            raise serializers.ValidationError('The value must not exceed 5')
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        representation['rating'] = instance.rating
        return representation
