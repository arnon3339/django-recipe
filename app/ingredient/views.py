"""View module for ingredient app."""
from .serializer import IngredientSerializer
from core.models import Ingredient

from rest_framework import viewsets
from rest_framework import authentication, permissions


class IngredientView(viewsets.ModelViewSet):
    """Ingedient view for ingredient app."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """return custom queryset."""
        return self.queryset.filter(user=self.request.user).order_by('name')
