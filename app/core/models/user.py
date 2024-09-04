""" Core app models. """
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
    )


class UserManager(BaseUserManager):
    """ User manager class. """
    def create_user(self, email, password=None, **fields):
        """ Create a user, save and return a new user."""
        user = self.model(email=self.normalize_email(email), **fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create a super user, save and return a new super user. """
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ User model. """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
