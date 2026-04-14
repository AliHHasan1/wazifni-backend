from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profile, Experience, Education, Skill, CV, Project, Certification
from jobs.models import Job
from django.conf import settings
import os
from .serializers import ProfileSerializer, ExperienceSerializer, EducationSerializer, SkillSerializer, CVSerializer, ProjectSerializer, CertificationSerializer
from services.ai_service import GeminiAIService

from django.shortcuts import get_object_or_404


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing candidate profiles."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """Retrieve or update the current authenticated user's profile."""
        profile = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class BaseProfileRelatedViewSet(viewsets.ModelViewSet):
    """Base ViewSet for profile-related models with automatic profile context injection."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(profile__user=self.request.user)

    def get_serializer_context(self):
        """Inject the user profile into serializer context for automatic assignment."""
        context = super().get_serializer_context()
        try:
            context["profile"] = self.request.user.candidate_profile
        except Profile.DoesNotExist:
            context["profile"] = None
        return context

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        # Handle bulk creation
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class ExperienceViewSet(BaseProfileRelatedViewSet):
    """ViewSet for managing work experience entries."""
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

    @action(detail=True, methods=["post"])
    def enhance_description(self, request, pk=None):
        """Enhance experience description using AI."""
        experience = self.get_object()

        if not experience.description:
            return Response(
                {"error": "No description to enhance. Please add a description first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_service = GeminiAIService()
            enhanced_text = ai_service.enhance_text(experience.description)
            experience.description = enhanced_text
            experience.save()
            experience.refresh_from_db()

            serializer = self.get_serializer(experience)
            return Response({
                "message": "Description enhanced successfully",
                "data": serializer.data
            })

        except Exception as e:
            return Response(
                {"error": f"AI service error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EducationViewSet(BaseProfileRelatedViewSet):
    """ViewSet for managing education entries."""
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class SkillViewSet(BaseProfileRelatedViewSet):
    """ViewSet for managing skills."""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ProjectViewSet(BaseProfileRelatedViewSet):
    """ViewSet for managing projects."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class CertificationViewSet(BaseProfileRelatedViewSet):
    """ViewSet for managing certifications."""
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class CVViewSet(viewsets.ModelViewSet):
    """ViewSet for generating and managing CVs with AI assistance."""
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(profile__user=self.request.user)

    @action(detail=False, methods=["post"], url_path="generate-general")
    def generate_general_cv(self, request):
        """Generate a general-purpose CV using AI, optimized for ATS systems."""
        try:
            profile = request.user.candidate_profile
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for this user. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)

        # Gather all profile data (including the new Project model data)
        profile_data = ProfileSerializer(profile).data

        ai_service = GeminiAIService()
        # Explicitly request English ATS-friendly content
        english_prompt = "Generate a comprehensive general CV in English, optimized for ATS, based on the provided profile data. Ensure all content is in English."
        try:
            general_cv_json = ai_service.generate_tailored_cv_content(profile_data, "", english_prompt)
        except Exception as e:
            return Response({"error_from_ai_service": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not general_cv_json:
            return Response({"error": "Failed to generate general CV content."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update existing general CV or create a new one
        general_cv, created = CV.objects.update_or_create(
            profile=profile,
            cv_type='general',
            defaults={
                "generated_json_content": general_cv_json,
                "generated_pdf_path": "" # Reset PDF path as content changed
            }
        )

        serializer = self.get_serializer(general_cv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="generate-job-specific")
    def generate_job_specific_cv(self, request):
        """Generate a job-specific CV tailored to a particular job description."""
        job_id = request.data.get("job_id")
        user_prompt = request.data.get("user_prompt", "")

        if not job_id:
            return Response({"error": "Job ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            profile = request.user.candidate_profile
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for this user. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)

        profile_data = ProfileSerializer(profile).data
        ai_service = GeminiAIService()
        job_description = job.description
        
        # Explicitly request English ATS-friendly content
        english_job_prompt = f"Generate a job-specific CV in English, optimized for ATS, based on the job description. Additional instructions: {user_prompt}. Ensure all content is in English."
        tailored_cv_json = ai_service.generate_tailored_cv_content(profile_data, job_description, english_job_prompt)

        if not tailored_cv_json:
            return Response({"error": "Failed to generate job-specific CV content."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update existing specific CV or create a new one
        job_specific_cv, created = CV.objects.update_or_create(
            profile=profile,
            job=job,
            cv_type='job_specific',
            defaults={
                "generated_json_content": tailored_cv_json,
                "generated_pdf_path": "" # Reset PDF path as content changed
            }
        )

        serializer = self.get_serializer(job_specific_cv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-pdf")
    def generate_cv_pdf(self, request, pk=None):
        """Generate a PDF document from existing CV JSON content."""
        cv_instance = self.get_object()
        if not cv_instance.generated_json_content:
            return Response({"error": "No CV content available to generate PDF."}, status=status.HTTP_400_BAD_REQUEST)

        from services.pdf_service import PDFService
        pdf_service = PDFService()

        output_filename = f"cv_{cv_instance.id}.pdf"
        output_path = os.path.join(settings.MEDIA_ROOT, "cv_pdfs", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            pdf_service.generate_cv_pdf(cv_instance.generated_json_content, output_path)
            cv_instance.generated_pdf_path = os.path.join("cv_pdfs", output_filename)
            cv_instance.save()
            return Response({"message": "PDF generated successfully", "pdf_url": cv_instance.generated_pdf_path}, status=status.HTTP_200_OK            )
        except Exception as e:
            return Response({"error": f"Failed to generate PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
