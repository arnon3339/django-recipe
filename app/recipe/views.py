"""View module for Recipe."""
from .serializer import RecipeDetailSerializer, RecipeSerializer
from core.models import Recipe

from rest_framework import viewsets, authentication, permissions


class RecipeView(viewsets.ModelViewSet):
    """Recipe view."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get recipes object data."""
        data = self.queryset.filter(user=self.request.user).order_by('-id')
        return data

    def get_serializer_class(self):
        "Return the serializer class for request."
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class
