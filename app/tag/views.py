"""View module for tag app."""
from core.models import Tag


from rest_framework import authentication, permissions
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from .serializer import TagSerializer


class TagView(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Generic API view of tag app."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get custom query set."""
        queryset = self.queryset.filter(user=self.request.user)
        id_params = self.request.query_params.get('id')

        if id_params:
            ids = [int(id_i) for id_i in id_params.split(',')]
            queryset = queryset.filter(id__in=ids)
        return queryset.order_by('name')
