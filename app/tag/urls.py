"""Urls module of tag app."""
from django.urls import path, include
from .views import TagView


from rest_framework.routers import DefaultRouter


routers = DefaultRouter()
routers.register('tags', TagView)


app_name = 'tag'


urlpatterns = [
    path('', include(routers.urls))
]
