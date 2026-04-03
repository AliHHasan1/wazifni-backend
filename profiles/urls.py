from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ExperienceViewSet, EducationViewSet, SkillViewSet, CVViewSet, ProjectViewSet, CertificationViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")
router.register(r"experiences", ExperienceViewSet)
router.register(r"education", EducationViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"certifications", CertificationViewSet) # Added for the new Certification model
router.register(r"cvs", CVViewSet)

urlpatterns = [
    path("", include(router.urls)),
]