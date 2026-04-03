from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ExperienceViewSet, EducationViewSet, SkillViewSet, CVViewSet, ProjectViewSet, CertificationViewSet
from django.urls import path
router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"experiences", ExperienceViewSet)
router.register(r"education", EducationViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"certifications", CertificationViewSet) # Added for the new Certification model
router.register(r"cvs", CVViewSet)

urlpatterns = router.urls
urlpatterns += [
    path("me/", ProfileViewSet.as_view({"get": "me", "patch": "me"}), name="profile-me"),
]
