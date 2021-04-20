from django.urls import path
from .views import *
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/<str:activation_code>/', ActivateView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('<slug:username>/', UserProfileView.as_view(),name='user-profile'),
    path('<slug:username>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('<slug:username>/get-followers/', GetFollowersView.as_view(), name='get-followers'),
    path('<slug:username>/get-following/', GetFollowingView.as_view(), name='get-following'),
]