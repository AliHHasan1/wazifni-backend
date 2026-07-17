from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Organization, User


class OrganizationRegistrationTests(APITestCase):
    def test_organization_registration_requires_verification_document(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "company",
                "email": "company@example.com",
                "password": "StrongPass123!",
                "user_type": "organization",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verification_document", response.data)

    def test_organization_registration_creates_pending_profile_with_document(self):
        document = SimpleUploadedFile(
            "identity.pdf",
            b"fake-pdf-content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "company",
                "email": "company@example.com",
                "password": "StrongPass123!",
                "user_type": "organization",
                "verification_document": document,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="company")
        organization = user.organization_profile
        self.assertEqual(organization.verification_status, Organization.VERIFICATION_STATUS_PENDING)
        self.assertTrue(organization.verification_document.name)

    def test_candidate_registration_does_not_require_verification_document(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "candidate",
                "email": "candidate@example.com",
                "password": "StrongPass123!",
                "user_type": "candidate",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrganizationProfileTests(APITestCase):
    def test_reuploading_verification_document_resets_status_to_pending(self):
        user = User.objects.create_user(
            username="company",
            email="company@example.com",
            password="StrongPass123!",
            user_type="organization",
        )
        organization = Organization.objects.create(
            user=user,
            name="Company",
            verification_status=Organization.VERIFICATION_STATUS_REJECTED,
            rejection_reason="Unreadable document",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            reverse("organization-profile"),
            {
                "verification_document": SimpleUploadedFile(
                    "new-identity.pdf",
                    b"new-fake-pdf-content",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        organization.refresh_from_db()
        self.assertEqual(organization.verification_status, Organization.VERIFICATION_STATUS_PENDING)
        self.assertEqual(organization.rejection_reason, "")
