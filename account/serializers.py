from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import send_activation_code
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from main.models import *
from rest_framework.settings import api_settings

'''REGISTER'''


class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user account"""
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'fullname', 'username', 'password', 'password_confirm')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5},
                        'username': {'min_length': 3}}

    def validate(self, validated_data):
        print(validated_data)
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return validated_data

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        user = get_user_model().objects.create_user(email=email, username=username, password=password)
        print(user.activation_code)
        send_activation_code(email=user.email, activation_code=user.activation_code)
        return user


'''LOGIN'''


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(label='Password', style={'input_type':'password'}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')

        if username and password and email:
            user = authenticate(request = self.context.get('request'), username = username, email=email, password = password)
            if not user:
                message = 'Unable to log in with provided credentials'
                raise serializers.ValidationError(message, code='authorization')
        else:
            message = 'Must include [email] and [password]'
            raise serializers.ValidationError(message, code='authorization')
        attrs['user'] = user
        return attrs


'''USER SETTINGS'''


#get, put, patch, delete methods for the user model
class UserInfoSerializer(serializers.ModelSerializer):
    """Serializer for the user settings objects"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'username', 'password',
                  'fullname', 'bio', 'profile_pic')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5},
                        'username': {'min_length': 3}}

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


'''POSTS'''


class UserPostsSerializer(serializers.ModelSerializer):
    """Serializer for viewing a user profile"""
    number_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'photo', 'text', 'location', 'number_of_likes',
                  'number_of_comments', 'posted_on')

    def get_number_of_comments(self, obj):
        return Comment.objects.filter(post=obj).count()


'''USER PROFILE'''


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing a user posts"""
    number_of_posts = serializers.SerializerMethodField()
    followed_by_req_user = serializers.SerializerMethodField()
    user_posts = serializers.SerializerMethodField('paginated_user_posts')

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'fullname',
                  'bio', 'profile_pic', 'number_of_followers',
                  'number_of_following', 'number_of_posts',
                  'user_posts', 'followed_by_req_user')

    def get_number_of_posts(self, obj):
        return Post.objects.filter(author=obj).count()

    def paginated_user_posts(self, obj):
        page_size = api_settings.PAGE_SIZE
        paginator = Paginator(obj.user_posts.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1

        user_posts = paginator.page(page)
        serializer = UserPostsSerializer(user_posts, many=True)

        return serializer.data

    def get_followed_by_req_user(self, obj):
        user = self.context['request'].user
        return user in obj.followers.all()


'''FOLLOWERS and FOLLOWING'''


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for listing all followers"""

    class Meta:
        model = get_user_model()
        fields = ('username', 'profile_pic')