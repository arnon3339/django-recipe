"""Urls module for ingredient app."""
from django.urls import path, include

from .views import IngredientView

from rest_framework.routers import DefaultRouter


routers = DefaultRouter()
routers.register('ingredients', IngredientView)


app_name = 'ingredient'


urlpatterns = [
    path('', include(routers.urls))
]
