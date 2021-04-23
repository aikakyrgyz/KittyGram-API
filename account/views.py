from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterUserSerializer, LoginUserSerializer, UserInfoSerializer, UserProfileSerializer, FollowSerializer, CreateNewPasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .utils import send_activation_email



'''PAGINATION'''


class FollowersLikersPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 5000


class PostsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentsPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20


'''REGISTRATION---POST'''


class RegisterUserView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Successfully registered", status=status.HTTP_201_CREATED)


'''ACTIVATION'''


class ActivateView(APIView):
    def get(self, request, activation_code):
        User = get_user_model()
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response("Your account is successfully activated", status=status.HTTP_200_OK)


'''LOGIN---POST'''


class LoginView(ObtainAuthToken):
    serializer_class = LoginUserSerializer


'''LOGOUT---POST'''


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Successfully logged out', status=status.HTTP_200_OK)


'''USER CRUD----GET, PUT, PATCH, DELETE'''


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated, ]


    def get_object(self):
        return self.request.user


'''USER VIEW --- GET '''
class UserProfileView(generics.RetrieveAPIView):
    lookup_field = 'username'
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.AllowAny,)


'''FOLLOW/UNFOLLOW ---GET '''
# 'api/account/<slug:username>/follow/'
# username = to_user
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, format=None, username=None):
        to_user = get_user_model().objects.get(username=username)
        from_user = self.request.user
        follow = None
        if from_user.is_authenticated:
            if from_user != to_user:
                if from_user in to_user.followers.all():
                    follow = False
                    from_user.following.remove(to_user)
                    to_user.followers.remove(from_user)
                else:
                    follow = True
                    from_user.following.add(to_user)
                    to_user.followers.add(from_user)
        data = {
            'follow': follow
        }
        return Response(data)


'''FOLLOWERS --- GET'''


# '<slug:username>/get-followers/'
class GetFollowersView(generics.ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = FollowersLikersPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = get_user_model().objects.get(
            username=username).followers.all()
        return queryset


'''FOLLOWING --- GET'''


# '<slug:username>/get-following/'
class GetFollowingView(generics.ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = FollowersLikersPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = get_user_model().objects.get(
            username=username).following.all()
        return queryset


#api/v1/account/forgot_password/
class ForgotPassword(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        User = get_user_model()
        user = get_object_or_404(User, email=email)
        user.is_active = False
        user.create_activation_code()
        user.save()
        send_activation_email(email=email, activation_code=user.activation_code)
        return Response('Activation code has been sent to your email', status=status.HTTP_200_OK)


class ForgotPasswordComplete(APIView):
    def post(self, request):
        data = request.data
        serializer = CreateNewPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('You have successfully reset your password', status=status.HTTP_200_OK)
