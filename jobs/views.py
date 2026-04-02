from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # Check if user is an organization and is approved by admin
        if request.user.user_type != 'organization':
            return Response({"error": "Only organizations can post jobs."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            org_profile = request.user.organization_profile

        except AttributeError:
            return Response({"error": "Organization profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization_profile)

    @action(detail=True, methods=["get"], url_path="applications")
    def applications(self, request, pk=None):
        job = self.get_object()
        # Ensure the requesting user is the owner of the job's organization
        if request.user.user_type != "organization" or job.organization.user != request.user:
            return Response({"error": "You do not have permission to view applications for this job."}, status=status.HTTP_403_FORBIDDEN)
        
        applications = job.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
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
        if request.user.user_type != 'candidate':
            return Response({"error": "Only candidates can apply for jobs."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the candidate is the current user
        request.data['candidate'] = request.user.id
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)
