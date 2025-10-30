from rest_framework import serializers
from form.models import Form, Category

class FormUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['title', 'description', 'category']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'category': {'required': False, 'allow_null': True},
        }

    def validate_title(self, value: str):
        if value is None:
            return value
        v = value.strip()
        if not v:
            raise serializers.ValidationError("Title cannot be empty.")
        if len(v) > 255:
            raise serializers.ValidationError("Title must be at most 255 characters.")
        return v

    def validate_category(self, value: Category | None):
        if value is None:
            return None
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if not (request.user.is_staff or request.user.is_superuser):
            if value.owner_id != request.user.id:
                raise serializers.ValidationError("You do not own this category.")
        return value
