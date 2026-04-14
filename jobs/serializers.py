from rest_framework import serializers
from .models import Job, Application
from users.serializers import OrganizationSerializer
from users.models import User


class JobSerializer(serializers.ModelSerializer):
    """Serializer for job postings with organization details."""
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='organization'), 
        source='organization', 
        write_only=True,
        required=False
    )

    class Meta:
        model = Job
        fields = '__all__'


class MyJobSerializer(serializers.ModelSerializer):
    """Serializer for organization to view their own jobs without organization details."""
    class Meta:
        model = Job
        exclude = ("organization",)


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications."""
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    candidate = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Application
        fields = '__all__'


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating application status."""
    status = serializers.ChoiceField(choices=["reviewed"])
