"""View module for ingredient app."""
from .serializer import IngredientSerializer
from core.models import Ingredient

from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework import authentication, permissions


class IngredientView(viewsets.ModelViewSet):
    """Ingedient view for ingredient app."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """return custom queryset."""
        queryset = self.queryset.filter(user=self.request.user)
        id_params = self.request.query_params.get('id')

        if id_params:
            ids = [int(id_i) for id_i in id_params.split(',')]
            queryset = queryset.filter(id__in=ids)
        return queryset.order_by('name')
