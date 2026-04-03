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

    def update_nested_field(self, instance, field_name, serializer_class, data):
        related_manager = getattr(instance, field_name)
        existing_items = {item.id: item for item in related_manager.all()}
        incoming_ids = []

        for item_data in data:
            item_id = item_data.get('id')
            context = {'profile': instance}
            if item_id and item_id in existing_items:
                # تحديث عنصر موجود
                item_instance = existing_items[item_id]
                serializer = serializer_class(item_instance, data=item_data, partial=True,context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                incoming_ids.append(item_id)
            else:
                # إنشاء عنصر جديد وربطه بالبروفايل
                serializer = serializer_class(data=item_data, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.save(profile=instance) # ربط مباشر بالبروفايل الحالي
                if serializer.instance:
                    incoming_ids.append(serializer.instance.id)

        # حذف العناصر التي لم ترسل في الطلب (لتحقيق مبدأ المزامنة)
        for eid in existing_items.keys():
            if eid not in incoming_ids:
                existing_items[eid].delete()
    def update(self, instance, validated_data):
        # Update direct fields on the Profile instance
        instance.bio = validated_data.get('bio', instance.bio)
        instance.portfolio = validated_data.get('portfolio', instance.portfolio)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.save()

        # Handle nested fields
        nested_fields_map = {
            'experiences': ExperienceSerializer,
            'education': EducationSerializer,
            'skills': SkillSerializer,
            'projects': ProjectSerializer,
            'certifications': CertificationSerializer,
        }

        for field_name, serializer_class in nested_fields_map.items():
            if field_name in validated_data:
                self.update_nested_field(instance, field_name, serializer_class, validated_data[field_name])

        return instance



    def create(self, validated_data):
        return super().create(validated_data)
