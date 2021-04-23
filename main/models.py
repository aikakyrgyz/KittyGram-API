from django.db import models
import uuid
from django.conf import settings
from account.models import image_file_path
from account.models import User


class Post(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False) #lookup
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_posts'
    )
    photo = models.ImageField(
        upload_to=image_file_path,
        blank=False,
        editable=False)
    text = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name="likers",
                                   blank=True,
                                   symmetrical=False)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='favoriters',
                                       blank=True,
                                       symmetrical=False)

    class Meta:
        ordering = ['-posted_on']

    def number_of_likes(self):
        if self.likes.count():
            return self.likes.count()
        else:
            return 0

    def __str__(self):
        return f'{self.author}\'s post'


class Comment(models.Model):
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='post_comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='user_comments')
    text = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_on']

    def __str__(self):
        return f'{self.author}\'s comment'


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_ratings')
    rating = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.post)+"---"+str(self.user)


class CatImages(models.Model):
    image_url = models.URLField(blank=True, null=True)
