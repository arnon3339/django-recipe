"""Recipe model module."""
import uuid
import os

from django.db import models
from django.contrib.auth import get_user_model


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = '{}{}'.format(uuid.uuid4(), ext)
    return os.path.join('uploads', 'recipe', filename)


class Recipe(models.Model):
    """Recipe model class."""
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    link = models.URLField(max_length=1024, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(upload_to=recipe_image_file_path, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='by_user_title', fields=['user',
                                                                  'title'])
        ]

    def __str__(self):
        return "{}(title={}, link={})".format(
            self.__class__.__name__, self.title, self.link
        )
