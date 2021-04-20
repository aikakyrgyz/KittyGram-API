import uuid #look
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


def image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/', filename)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(email=self.normalize_email(email),
                          username=username.lower(),
                          **extra_fields)
        user.set_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    fullname = models.CharField(max_length=60, blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(
        upload_to=image_file_path,
        default='avatar.png')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name="user_followers",
                                       blank=True,
                                       symmetrical=False)
    following = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name="user_following",
                                       blank=True,
                                       symmetrical=False)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def number_of_followers(self):
        if self.followers.count():
            return self.followers.count()
        else:
            return 0

    def number_of_following(self):
        if self.following.count():
            return self.following.count()
        else:
            return 0

    def create_activation_code(self):
        # 1. hashlib.md5(self.email + str(self.id)).encode() ->hexdigest()
        # 2. get_random_string(50, allowed_char=['']
        # 3. UUID
        # 4. datetime.datetime.now() or time.time() + timestamp()
        import hashlib
        string = self.email + str(self.id)
        encode_string = string.encode()
        md5_object = hashlib.md5(encode_string)
        activation_code = md5_object.hexdigest()
        self.activation_code = activation_code

    def __str__(self):
        return self.username
