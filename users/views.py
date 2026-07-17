from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, OrganizationSerializer, MyTokenObtainPairSerializer
from .models import User, Organization
from profiles.models import Profile


class MyTokenObtainPairView(TokenObtainPairView):
    """Custom token view that includes user type in JWT token."""

    serializer_class = MyTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """Registration endpoint that automatically creates profile or organization based on user type."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_create(self, serializer):
        """Automatically create associated profile based on user type."""
        verification_document = serializer.validated_data.get("verification_document")
        user = serializer.save()
        if user.user_type == 'candidate':
            Profile.objects.get_or_create(user=user)
        elif user.user_type == 'organization':
            Organization.objects.get_or_create(
                user=user,
                defaults={
                    "name": user.username,
                    "verification_document": verification_document,
                },
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for users to retrieve and update their own profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class OrganizationProfileView(generics.RetrieveUpdateAPIView):
    """View for organizations to retrieve and update their organization profile."""
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_object(self):
        """Return organization profile, creating one if it does not exist."""
        if self.request.user.user_type != "organization":
            raise PermissionDenied("Only organization users can have an organization profile.")
        org, created = Organization.objects.get_or_create(user=self.request.user, defaults={'name': self.request.user.username})
        return org

    def update(self, request, *args, **kwargs):
        """Only organization users can update their organization profile."""
        if self.request.user.user_type != 'organization':
            return Response({"error": "Only organization users can have an organization profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
