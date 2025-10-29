from rest_framework import serializers
from form.models import (
    Form,
    Answer,
    Process,
    Category,
    Question,
    ProcessForm,
)


# --------------------------------------------
# (Process Detail)
# --------------------------------------------

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


# --------------------------------------------
# (Process Build)
# --------------------------------------------

class ProcessFormInputSerializer(serializers.Serializer):
    """Used for creating process-forms relations"""
    form_id = serializers.IntegerField()
    order_index = serializers.IntegerField()


class ProcessBuildSerializer(serializers.ModelSerializer):
    """Used for creating a new process along with related forms"""
    forms = ProcessFormInputSerializer(many=True, write_only=True)

    class Meta:
        model = Process
        fields = [
            'name', 'description', 'category',
            'is_public', 'access_password_hash',
            'process_type', 'forms'
        ]
    
    def create(self, validated_data):
        forms_data = validated_data.pop('forms', [])
        user = self.context['request'].user
        process = Process.objects.create(creator=user, **validated_data)

        # Link forms to process
        for form_data in forms_data:
            ProcessForm.objects.create(
                process=process,
                form_id=form_data['form_id'],
                order_index=form_data['order_index']
            )

        return process