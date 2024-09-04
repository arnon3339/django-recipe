"""View module for user app."""
from .serializer import UserSerializer, AuthenticationSerializer

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthenticationSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class MangeUserView(generics.RetrieveUpdateAPIView):
    """Manage the authentication user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrive and return the authenticated user."""
        return self.request.user
