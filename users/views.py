from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, OrganizationSerializer, MyTokenObtainPairSerializer
from .models import User, Organization
from profiles.models import Profile

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Automatically create a Profile for candidate users
        if user.user_type == 'candidate':
            Profile.objects.get_or_create(user=user)
        # Automatically create an Organization profile for organization users
        elif user.user_type == 'organization':
            Organization.objects.get_or_create(user=user, name=user.username)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class OrganizationProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure user has an organization profile
        org, created = Organization.objects.get_or_create(user=self.request.user, defaults={'name': self.request.user.username})
        return org

    def update(self, request, *args, **kwargs):
        if self.request.user.user_type != 'organization':
            return Response({"error": "Only organization users can have an organization profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
