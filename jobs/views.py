from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Job, Application
from .serializers import (
    JobSerializer,
    MyJobSerializer,
    ApplicationSerializer,
    ApplicationStatusUpdateSerializer,
)


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job postings and applications."""
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_queryset(self):
        if self.action == "list":
            return Job.objects.filter(application_deadline__gte=timezone.now().date())
        return super().get_queryset()

    FINAL_APPLICATION_STATUSES = {"accepted", "rejected"}

    def get_serializer_class(self):
        if self.action == "my_jobs":
            return MyJobSerializer
        return super().get_serializer_class()

    def _get_owned_job_application(self, request, job, application_id):
        """Verify that the requesting user owns the job and return the application."""
        if request.user.user_type != "organization" or job.organization.user != request.user:
            return None, Response(
                {"error": "You do not have permission to update applications for this job."},
                status=status.HTTP_403_FORBIDDEN,
            )

        application = get_object_or_404(job.applications, pk=application_id)
        return application, None

    def _set_application_status(self, application, new_status):
        """Update application status with validation to prevent changing finalized applications."""
        if application.status in self.FINAL_APPLICATION_STATUSES:
            return Response(
                {
                    "error": (
                        "This application has already been finalized and its status "
                        "can no longer be changed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if application.status == new_status:
            return Response(
                {"error": f"Application is already marked as {new_status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = new_status
        application.save(update_fields=["status"])
        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Create a new job posting. Only organizations can post jobs."""
        if request.user.user_type != 'organization':
            return Response({"error": "Only organizations can post jobs."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            org_profile = request.user.organization_profile

        except AttributeError:
            return Response({"error": "Organization profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization_profile)

    @action(
        detail=False,
        methods=["get"],
        url_path="my-jobs",
        permission_classes=[permissions.IsAuthenticated],
    )
    def my_jobs(self, request):
        """List all jobs posted by the authenticated organization."""
        if request.user.user_type != "organization":
            return Response(
                {"error": "Only organizations can view their posted jobs."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            org_profile = request.user.organization_profile
        except AttributeError:
            return Response(
                {"error": "Organization profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = self.get_queryset().filter(organization=org_profile).order_by("-posted_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="applications")
    def applications(self, request, pk=None):
        """List all applications for a specific job (organization owner only)."""
        job = self.get_object()
        if request.user.user_type != "organization" or job.organization.user != request.user:
            return Response({"error": "You do not have permission to view applications for this job."}, status=status.HTTP_403_FORBIDDEN)
        
        applications = job.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["patch"],
        url_path=r"applications/(?P<application_id>[^/.]+)/status",
        permission_classes=[permissions.IsAuthenticated],
    )
    def update_application_status(self, request, pk=None, application_id=None):
        """Update application status to any valid status (organization owner only)."""
        job = self.get_object()
        application, error_response = self._get_owned_job_application(request, job, application_id)
        if error_response is not None:
            return error_response

        status_serializer = ApplicationStatusUpdateSerializer(data=request.data)
        status_serializer.is_valid(raise_exception=True)
        return self._set_application_status(
            application,
            status_serializer.validated_data["status"],
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path=r"applications/(?P<application_id>[^/.]+)/accept",
        permission_classes=[permissions.IsAuthenticated],
    )
    def accept_application(self, request, pk=None, application_id=None):
        """Accept a job application (organization owner only)."""
        job = self.get_object()
        application, error_response = self._get_owned_job_application(request, job, application_id)
        if error_response is not None:
            return error_response

        return self._set_application_status(application, "accepted")

    @action(
        detail=True,
        methods=["patch"],
        url_path=r"applications/(?P<application_id>[^/.]+)/reject",
        permission_classes=[permissions.IsAuthenticated],
    )
    def reject_application(self, request, pk=None, application_id=None):
        """Reject a job application (organization owner only)."""
        job = self.get_object()
        application, error_response = self._get_owned_job_application(request, job, application_id)
        if error_response is not None:
            return error_response

        return self._set_application_status(application, "rejected")


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications submitted by candidates."""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter applications based on user type (candidates see their own, organizations see theirs)."""
        queryset = self.queryset
        user = self.request.user

        if user.user_type == "candidate":
            queryset = queryset.filter(candidate=user)
        elif user.user_type == "organization":
            queryset = queryset.filter(job__organization__user=user)
        else:
            return queryset.none()

        job_id = self.request.query_params.get("job_id")
        if job_id:
            # Ensure the organization can only filter by its own jobs
            if user.user_type == "organization":
                queryset = queryset.filter(job__id=job_id, job__organization__user=user)
            else:
                # Candidates cannot filter by job_id for applications they didn't make
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        """Submit a new job application. Only candidates can apply."""
        if request.user.user_type != 'candidate':
            return Response({"error": "Only candidates can apply for jobs."}, status=status.HTTP_403_FORBIDDEN)
        
        job_id = request.data.get("job")
        if not job_id:
            return Response({"error": "Job ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if job.application_deadline < timezone.now().date():
            return Response({"error": "Application deadline has passed."}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data['candidate'] = request.user.id
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)

    def update(self, request, *args, **kwargs):
        """Direct updates are not allowed. Applications can only be updated via job endpoints."""
        return Response(
            {
                "error": (
                    "Direct application updates are not allowed. "
                    "Use the job application review, accept, or reject endpoints."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
