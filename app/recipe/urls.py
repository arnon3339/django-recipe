"""Urls module of recipe app."""
from django.urls import path, include

from .views import RecipeView

from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register('recipes', RecipeView)

app_name = 'recipe'

urlpatterns = [
    path('', include(routers.urls))
]
