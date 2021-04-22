from rest_framework import permissions, viewsets, generics, status
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, RatingSerializer
from account.views import FollowersLikersPagination
from .models import Post, Comment, Rating
from .permissions import IsOwnerOrReadOnly, IsOwnerOrPostOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated


'''CREATE POST --- POST'''
# localhost:8000/api/post/
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = (
        IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    # filtering using queryset by the date
    @action(detail=False, methods=['get'])
    def recent(self, request, pk=None):
        queryset = self.queryset
        days_count = int(self.request.query_params.get('days', default=0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    #filtering by my posts using action decorator, url -> v1/api/post/own/
    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    #search
    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        # print(request.query_params)
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(text__icontains=q)|Q(location__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

'''LENTA --- GET '''
class UserFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        user = self.request.user
        print(user)
        following_users = user.following.all()
        queryset = Post.objects.all().filter(author__in=following_users)
        return queryset


'''GET THE LIST OF FAVORITE POSTS --- GET '''
class UserFavoritesView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        user = self.request.user
        favorited_posts = user.favoriters.all()
        queryset = Post.objects.all().filter(pk__in=favorited_posts)
        print(queryset)
        return queryset


'''COMMENT POST --- POST, [text]'''
class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, post_id=None):
        post = Post.objects.get(pk=post_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)



'''CHANGE commentT --- GET, PATCH, DELETE '''
class ManageCommentView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    lookup_url_kwarg = 'comment_id'
    permission_classes = (IsOwnerOrPostOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.all()
        return queryset


'''LIKE/UNLIKE POST --- GET '''
class LikeView(APIView):
    def get(self, request, format=None, post_id=None):
        post = Post.objects.get(pk=post_id)
        user = self.request.user
        if user.is_authenticated:
            if user in post.likes.all():
                like = False
                post.likes.remove(user)
            else:
                like = True
                post.likes.add(user)
        data = {
            'like': like
        }
        return Response(data)


'''FAVORITE/UNFAVORITE POST --- GET '''
class FavoriteView(APIView):
    def get(self, request, format=None, post_id=None):
        post = Post.objects.get(pk=post_id)
        user = self.request.user
        if user.is_authenticated:
            if user in post.favorites.all():
                favorite = False
                post.favorites.remove(user)
            else:
                favorite = True
                post.favorites.add(user)
            data = {
                'favorite': favorite
            }
            return Response(data)


'''GET THE LIST OF LIKERS --- GET '''
class GetLikersView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    pagination_class = FollowersLikersPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        queryset = Post.objects.get(
            pk=post_id).likes.all()
        return queryset


'''GET THE LIST OF FAVORITERS --- GET '''
class GetFavoritersView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    pagination_class = FollowersLikersPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        queryset = Post.objects.get(
            pk=post_id).favorites.all()
        return queryset



class RatingViewSet(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]


    def post(self, request, post_id=None):
        post = Post.objects.get(pk=post_id)
        user = self.request.user
        post_rating = Rating.objects.filter(post=post, user=user)
        if not post_rating:
            serializer = RatingSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(post=post, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('You have already rated this post', status=status.HTTP_403_FORBIDDEN)

