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
        return self.queryset.filter(user=self.request.user).order_by('name')
