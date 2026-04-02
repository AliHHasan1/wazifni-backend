from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegisterView, 
    MyTokenObtainPairView, 
    UserProfileView, 
    OrganizationProfileView
)

urlpatterns = [
    # Auth Endpoints
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Profile Endpoints
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("organization/me/", OrganizationProfileView.as_view(), name="organization-profile"),
]
