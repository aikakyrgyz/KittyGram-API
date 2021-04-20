from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register('', PostViewSet)
# app_name = 'post'

urlpatterns = [
    path('feed/', UserFeedView.as_view(), name='feed'),
    path('', include(router.urls)),
    path('comment/<uuid:post_id>/', AddCommentView.as_view(), name='add-comment'),
    path('comment/<int:comment_id>/', ManageCommentView.as_view(), name='manage-comment'),
    path('like/<uuid:post_id>/', LikeView.as_view(), name='like'),
    path('<uuid:post_id>/get-likers/', GetLikersView.as_view(), name='get-likers'),
    ]