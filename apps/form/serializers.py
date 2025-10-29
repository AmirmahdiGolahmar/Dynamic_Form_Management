from rest_framework import serializers
from form.models import (
    Form,
    Answer,
    Process,
    Category,
    Question,
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_info', 'is_required', 'order_index']


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'category_name',
            'is_public', 'created_at', 'updated_at', 'questions'
        ]


class ProcessDetailSerializer(serializers.ModelSerializer):
    forms = FormSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = Process
        fields = [
            'id', 'name', 'description', 'process_type',
            'is_public', 'created_at', 'updated_at',
            'category_name', 'creator_name', 'forms'
        ]
