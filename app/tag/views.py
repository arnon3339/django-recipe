"""View module for tag app."""
from core.models import Tag


from rest_framework import authentication, permissions
from rest_framework import viewsets, mixins


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
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get custom query set."""
        queryset = self.queryset.filter(user=self.request.user)
        id_params = self.request.query_params.get('id')
        name_params = self.request.query_params.get('name')

        if id_params:
            ids = [int(id_i) for id_i in id_params.split(',')]
            queryset = queryset.filter(id__in=ids)
        if name_params:
            names = name_params.split(',')
            queryset = queryset.filter(name__in=names)

        return queryset.order_by('name')
