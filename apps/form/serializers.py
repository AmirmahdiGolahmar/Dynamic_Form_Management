from rest_framework import serializers
from form.models import (
    Form,
    Answer,
    Process,
    Category,
    Question,
    ProcessForm,
)



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





# --------------------------------------------
# (Process Detail)
# --------------------------------------------

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_info', 'is_required', 'order_index']

FormSerializer
class FormSerializer(serializers.ModelSerializer):
    # Each form can have one question (one-to-one)
    question = QuestionSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'category_name',
            'is_public', 'created_at', 'updated_at', 'question'
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
# (Process Build / Create)
# --------------------------------------------

class ProcessFormInputSerializer(serializers.Serializer):
    form_id = serializers.IntegerField()
    order_index = serializers.IntegerField()


class ProcessBuildSerializer(serializers.ModelSerializer):
    forms = ProcessFormInputSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Process
        fields = [
           'id', 'name', 'description', 'category',
            'is_public', 'access_password_hash',
            'process_type', 'forms'
        ]

    def create(self, validated_data):
        forms_data = validated_data.pop('forms', [])
        user = self.context['request'].user
        process = Process.objects.create(creator=user, **validated_data)
        for form_data in forms_data:
            ProcessForm.objects.create(
                process=process,
                form_id=form_data['form_id'],
                order_index=form_data['order_index']
            )
        return process
class ProcessWelcomeSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Process
        fields = ['id', 'title']



class ProcessEndSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)
    class Meta:
        model = Process
        fields = ['id', 'title']


class ProcessSubmitSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Process
        fields = ['id', 'title']


class ProcessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['process_type', 'is_public', 'access_password_hash']
        extra_kwargs = {
            'access_password_hash': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        if not data.get('is_public', True) and not data.get('access_password_hash'):
            raise serializers.ValidationError("Private process must have a password.")
        return data
 
