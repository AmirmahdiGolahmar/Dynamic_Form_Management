from rest_framework import serializers

from .models import Form


class FormSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Form
        fields = [
            'id',
            'title', #input
            'description', #input
            'creator',
            'category', #input
            'is_public', #input
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']