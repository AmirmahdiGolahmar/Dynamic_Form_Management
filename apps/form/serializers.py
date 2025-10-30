from rest_framework import serializers
from .models import Form, Category

class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',           # input
            'description',    # input
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class FormSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Form
        fields = [
            'id',
            'title',      # input
            'description',# input
            'creator',
            'category',   # input
            'is_public',  # input
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']
