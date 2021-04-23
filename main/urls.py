from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register('', PostViewSet)

urlpatterns = [
    path('feed/', UserFeedView.as_view(), name='feed'),
    path('myfavorites/', UserFavoritesView.as_view(), name='favorites'),
    path('', include(router.urls)),
    path('comment/<uuid:post_id>/', AddCommentView.as_view(), name='add-comment'),
    path('comment/<int:comment_id>/', ManageCommentView.as_view(), name='manage-comment'),
    path('rate/<uuid:post_id>/', RatingViewSet.as_view(), name='rate-post'),
    path('like/<uuid:post_id>/', LikeView.as_view(), name='like'),
    path('<uuid:post_id>/get-likers/', GetLikersView.as_view(), name='get-likers'),
    path('favorite/<uuid:post_id>/', FavoriteView.as_view(), name='favorite'),
    path('<uuid:post_id>/get-favoriters/', GetFavoritersView.as_view(), name='get-favoriters'),

]