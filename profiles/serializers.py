from rest_framework import serializers
from .models import Profile, Experience, Education, Skill, CV, Project, Certification
from users.serializers import UserSerializer


class BaseProfileRelatedSerializer(serializers.ModelSerializer):
    """Base serializer for profile-related models with automatic profile assignment."""

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
    """Serializer for work experience entries."""
    class Meta:
        model = Experience
        exclude = ('profile',)

class EducationSerializer(BaseProfileRelatedSerializer):
    """Serializer for education entries."""
    class Meta:
        model = Education
        exclude = ('profile',)

class SkillSerializer(BaseProfileRelatedSerializer):
    """Serializer for skill entries."""
    class Meta:
        model = Skill
        exclude = ('profile',)

class ProjectSerializer(BaseProfileRelatedSerializer):
    """Serializer for project entries."""
    class Meta:
        model = Project
        exclude = ('profile',)

class CertificationSerializer(BaseProfileRelatedSerializer):
    """Serializer for certification entries."""
    class Meta:
        model = Certification
        exclude = ('profile',)

class CVSerializer(serializers.ModelSerializer):
    """Serializer for CV entries containing generated content."""
    generated_json_content = serializers.JSONField(required=False)

    class Meta:
        model = CV
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    """Main profile serializer with nested support for all related data."""
    user = UserSerializer(read_only=True)
    experiences = ExperienceSerializer(many=True, required=False)
    education = EducationSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)
    cvs = CVSerializer(many=True, read_only=True)

    portfolio = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True) # New field for LinkedIn

    class Meta:
        model = Profile
        fields = "__all__"

    def update_nested_field(self, instance, field_name, serializer_class, data):
        """Full state sync: creates, updates, or deletes nested related items based on incoming data."""
        related_manager = getattr(instance, field_name)
        existing_items = {item.id: item for item in related_manager.all()}
        incoming_ids = set()

        for item_data in data:
            raw_id = item_data.get('id')
            item_id = int(raw_id) if raw_id is not None else None
            
            context = {'profile': instance}
            
            if item_id and item_id in existing_items:
                incoming_ids.add(item_id)
                item_instance = existing_items[item_id]
                serializer = serializer_class(item_instance, data=item_data, partial=True, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:

                create_data = item_data.copy()
                create_data.pop('id', None)
                serializer = serializer_class(data=create_data, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        existing_ids = set(existing_items.keys())
        ids_to_delete = existing_ids - incoming_ids
        if ids_to_delete:
            related_manager.filter(id__in=ids_to_delete).delete()

    def update(self, instance, validated_data):
        nested_fields_map = {
            'experiences': ExperienceSerializer,
            'education': EducationSerializer,
            'skills': SkillSerializer,
            'projects': ProjectSerializer,
            'certifications': CertificationSerializer,
        }

        nested_data = {}
        for field_name in nested_fields_map.keys():
            if field_name in validated_data:
                nested_data[field_name] = validated_data.pop(field_name)

        instance.bio = validated_data.get('bio', instance.bio)
        instance.portfolio = validated_data.get('portfolio', instance.portfolio)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.save()

        for field_name, serializer_class in nested_fields_map.items():
            if field_name in nested_data:
                self.update_nested_field(instance, field_name, serializer_class, nested_data[field_name])

        return instance

    def create(self, validated_data):
        return super().create(validated_data)
