from rest_framework import serializers
from .models import Profile, Experience, Education, Skill, CV, Project, Certification
from users.serializers import UserSerializer

class BaseProfileRelatedSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        profile = self.context.get("profile")
        if not profile:
            raise serializers.ValidationError({"detail": "Profile context is missing."})
        return self.Meta.model.objects.create(profile=profile, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ExperienceSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Experience
        fields = "__all__"

class EducationSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Education
        fields = "__all__"

class SkillSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Skill
        fields = "__all__"

class ProjectSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Project
        fields = "__all__"

class CertificationSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Certification
        fields = "__all__" # Removed expiration_date and is_current from model, so __all__ will reflect that

class CVSerializer(serializers.ModelSerializer):
    generated_json_content = serializers.JSONField(required=False)

    class Meta:
        model = CV
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    experiences = ExperienceSerializer(many=True, required=False)
    education = EducationSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False) # New field
    cvs = CVSerializer(many=True, read_only=True)

    portfolio = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True) # New field for LinkedIn

    class Meta:
        model = Profile
        fields = "__all__"

    def create_or_update_nested(self, instance, related_model, related_serializer, data):
        existing_ids = set(item.id for item in getattr(instance, related_model._meta.related_name).all())
        incoming_ids = set()
        
        for item_data in data:
            item_id = item_data.get("id")
            if item_id:
                incoming_ids.add(item_id)
                try:
                    item_instance = getattr(instance, related_model._meta.related_name).get(id=item_id)
                    serializer = related_serializer(item_instance, data=item_data, partial=True, context={"profile": instance})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except related_model.DoesNotExist:
                    serializer = related_serializer(data=item_data, context={"profile": instance})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
            else:
                serializer = related_serializer(data=item_data, context={"profile": instance})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        
        for item_id_to_delete in existing_ids - incoming_ids:
            getattr(instance, related_model._meta.related_name).filter(id=item_id_to_delete).delete()

    def update(self, instance, validated_data):
        instance.bio = validated_data.get("bio", instance.bio)
        instance.portfolio = validated_data.get("portfolio", instance.portfolio)
        instance.linkedin = validated_data.get("linkedin", instance.linkedin) # Update linkedin field
        instance.save()

        nested_fields = {
            "experiences": (Experience, ExperienceSerializer),
            "education": (Education, EducationSerializer),
            "skills": (Skill, SkillSerializer),
            "projects": (Project, ProjectSerializer),
            "certifications": (Certification, CertificationSerializer),
        }

        for field_name, (model, serializer_class) in nested_fields.items():
            if field_name in validated_data:
                self.create_or_update_nested(instance, model, serializer_class, validated_data[field_name])

        return instance



    def create(self, validated_data):
        return super().create(validated_data)
