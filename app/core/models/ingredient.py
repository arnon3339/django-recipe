"""Ingredient model module."""
from django.db import models
from django.conf import settings


class Ingredient(models.Model):
    """Ingredient class model."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='by_user_name',
                                    fields=['user', 'name'])
        ]

    def __str__(self):
        return "{}(name={})".format(self.__class__.__name__,
                                    self.name)
