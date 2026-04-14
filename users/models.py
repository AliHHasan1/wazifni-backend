from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model supporting multiple user types (candidate, organization, admin)."""
    USER_TYPE_CHOICES = (
        ("candidate", "Candidate"),
        ("organization", "Organization"),
        ("admin", "Admin"),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="candidate")
    email = models.EmailField(unique=True, blank=False, null=False, default="example@example.com") # Make email unique
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username


class Organization(models.Model):
    """Organization profile linked to a user account."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="organization_profile")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
