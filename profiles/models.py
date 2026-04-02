from django.db import models
from users.models import User
from jobs.models import Job

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="candidate_profile")
    bio = models.TextField(blank=True, null=True)
    portfolio = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True) # New field for LinkedIn

    def __str__(self):
        return self.user.username

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} at {self.company}"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"

class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    technologies = models.JSONField(default=list, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Certification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} from {self.issuing_organization}"

class CV(models.Model):
    CV_TYPE_CHOICES = [
        ("general", "General CV"),
        ("job_specific", "Job-Specific CV"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="cvs")
    job = models.ForeignKey("jobs.Job", on_delete=models.SET_NULL, null=True, blank=True, related_name="tailored_cvs")
    cv_type = models.CharField(max_length=20, choices=CV_TYPE_CHOICES, default="general")
    generated_pdf_path = models.CharField(max_length=255, blank=True, null=True)
    generated_json_content = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"
        unique_together = ("profile", "job", "cv_type")

    def __str__(self):
        if self.cv_type == "general":
            return f"General CV for {self.profile.user.username}"
        return f"Job-Specific CV for {self.profile.user.username} - {self.job.title}"
