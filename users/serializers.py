from rest_framework import serializers
from .models import User, Organization
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and profile data."""
    full_name = serializers.SerializerMethodField()
    verification_document = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "phone_number",
            "address",
            "password",
            "verification_document",
        )
        read_only_fields = ("id", "full_name",)
        extra_kwargs = {"password": {"write_only": True}}

    def get_full_name(self, obj):
        return obj.get_full_name()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("user_type") == "organization" and not attrs.get("verification_document"):
            raise serializers.ValidationError(
                {
                    "verification_document": (
                        "Verification document is required when registering "
                        "an organization account."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("verification_document", None)
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organization profile with nested user data."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Organization
        fields = (
            "user",
            "name",
            "description",
            "location",
            "verification_document",
            "verification_status",
            "verified_at",
            "rejection_reason",
        )
        read_only_fields = ("user", "verification_status", "verified_at", "rejection_reason")

    def update(self, instance, validated_data):
        if "verification_document" in validated_data:
            instance.verification_status = Organization.VERIFICATION_STATUS_PENDING
            instance.verified_at = None
            instance.rejection_reason = ""
        return super().update(instance, validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user type and username in token claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_type'] = user.user_type
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
