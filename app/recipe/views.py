"""View module for Recipe."""
from .serializer import (
    RecipeDetailSerializer, RecipeSerializer, ImageSerializer
)
from core.models import Recipe

from rest_framework import (
    viewsets, authentication, permissions,
    status, response
)
from rest_framework.decorators import action


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
        elif self.action == 'upload_image':
            return ImageSerializer

        return self.serializer_class

    @action(methods=['post'], url_path='upload-image', detail=True)
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data,
                                     status.HTTP_200_OK)
        return response.Response(serializer.errors,
                                 status.HTTP_400_BAD_REQUEST)
