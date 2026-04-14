from django.db import models
from users.models import User, Organization


class Job(models.Model):
    """Job posting created by an organization."""
    JOB_TYPE_CHOICES = (
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("remote", "Remote"),
        ("internship", "Internship"),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    skills_required = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default="full_time")
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    application_deadline = models.DateField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    """Job application submitted by a candidate."""
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("reviewed", "Reviewed"),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    cv_file = models.FileField(upload_to='applications/cvs/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "candidate") # Ensure a candidate can only apply once per job

    def __str__(self):
        return f"Application for {self.job.title} by {self.candidate.username}"

