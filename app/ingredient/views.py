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
        queryset = self.queryset.filter(user=self.request.user)
        filter_params = {}
        for k, v in self.request.query_params.items():
            filter_params['{}'.format(k + '__in')] =\
                [int(v_i) if k == 'id' else v_i for v_i in v.split(',')]
        return queryset.filter(**filter_params).order_by('name')
