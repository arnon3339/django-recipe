"""Tag model module."""
from django.db import models
from django.contrib.auth import get_user_model


class Tag(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=256, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_by_user_name',
                                    fields=['user', 'name'])
        ]

    def __str__(self):
        return "{}(name={})".format(self.__class__.__name__, self.name)
