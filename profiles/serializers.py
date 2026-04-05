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
        exclude = ('profile',)

class EducationSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Education
        exclude = ('profile',)

class SkillSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Skill
        exclude = ('profile',)

class ProjectSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Project
        exclude = ('profile',)

class CertificationSerializer(BaseProfileRelatedSerializer):
    class Meta:
        model = Certification
        exclude = ('profile',)

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

    def update_nested_field(self, instance, field_name, serializer_class, data):
        """
        Logic for Full State Sync:
        1. Identify existing items in the database.
        2. Identify items to update (have an ID present in DB).
        3. Identify items to create (no ID or ID not in DB).
        4. Identify items to delete (in DB but missing from the request).
        """
        related_manager = getattr(instance, field_name)
        existing_items = {item.id: item for item in related_manager.all()}
        incoming_ids = set()

        for item_data in data:
            # Ensure ID is an integer if it exists
            raw_id = item_data.get('id')
            item_id = int(raw_id) if raw_id is not None else None
            
            context = {'profile': instance}
            
            if item_id and item_id in existing_items:
                # ✅ Update existing item
                incoming_ids.add(item_id)
                item_instance = existing_items[item_id]
                serializer = serializer_class(item_instance, data=item_data, partial=True, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # ✅ Create new item (ignore invalid or missing IDs)
                # Create a copy to avoid modifying original data if needed elsewhere
                create_data = item_data.copy()
                create_data.pop('id', None)
                serializer = serializer_class(data=create_data, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        # 🗑️ Delete items that were in DB but NOT in the incoming request
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

        # 💥 اسحب nested data قبل ما تخرب الدنيا
        nested_data = {}
        for field_name in nested_fields_map.keys():
            if field_name in validated_data:
                nested_data[field_name] = validated_data.pop(field_name)

        # Update normal fields
        instance.bio = validated_data.get('bio', instance.bio)
        instance.portfolio = validated_data.get('portfolio', instance.portfolio)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.save()

        # Update nested بعد ما فصلناهم
        for field_name, serializer_class in nested_fields_map.items():
            if field_name in nested_data:
                self.update_nested_field(instance, field_name, serializer_class, nested_data[field_name])

        return instance



    def create(self, validated_data):
        return super().create(validated_data)
