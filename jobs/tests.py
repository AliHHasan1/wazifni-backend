from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Organization, User


class JobPostingVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="company",
            email="company@example.com",
            password="StrongPass123!",
            user_type="organization",
        )
        self.organization = Organization.objects.create(user=self.user, name="Company")
        self.payload = {
            "title": "Backend Developer",
            "description": "Build and maintain APIs.",
            "requirements": "Django and DRF experience.",
            "job_type": "full_time",
            "location": "Baghdad",
            "application_deadline": (timezone.now().date() + timedelta(days=30)).isoformat(),
        }

    def test_pending_organization_cannot_post_job(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse("job-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["verification_status"], Organization.VERIFICATION_STATUS_PENDING)

    def test_approved_organization_can_post_job(self):
        self.organization.verification_status = Organization.VERIFICATION_STATUS_APPROVED
        self.organization.verified_at = timezone.now()
        self.organization.save(update_fields=["verification_status", "verified_at"])
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse("job-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.payload["title"])
