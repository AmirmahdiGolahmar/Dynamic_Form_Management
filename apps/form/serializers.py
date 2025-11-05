from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from form.models import (
    Form,
    Answer,
    Process,
    Category,
    Question,
    ProcessForm,
)


# --------------------------------------------
# JSON Schema Convention for Question & Answer
# --------------------------------------------
# question_info (on Question model):
# {
#   "type": "text" | "select" | "checkbox",
#   // if type = text:
#   "placeholder": "optional",
#   "min_length": 0,
#   "max_length": 255,
#   "regex": "optional"
#   // if type = select or checkbox:
#   "options": [
#     {"id": "opt1", "label": "Option 1", "value": "optional"},
#     ...
#   ],
#   // select behaves like checkbox but with max_select = 1
#   "min_select": 0,
#   "max_select": 1 | n
# }
#
# answer_json (on Answer model):
# - text:      {"value": "text answer"}
# - select:    {"value": "opt_id"}
# - checkbox:  {"values": ["opt_id_1", "opt_id_2", ...]}
# --------------------------------------------

# --------------------------------------------
# question_info schema validator
# --------------------------------------------
def validate_question_info_schema(info: dict):
    """Validate structure and logic of question_info JSON."""
    if not isinstance(info, dict):
        raise serializers.ValidationError("question_info must be a JSON object.")
    qtype = (info.get('type') or '').lower()
    if qtype not in ('text', 'select', 'checkbox'):
        raise serializers.ValidationError("question_info.type must be one of: text, select, checkbox.")

    if qtype in ('select', 'checkbox'):
        options = info.get('options', [])
        if not isinstance(options, list) or not options:
            raise serializers.ValidationError("options must be a non-empty list for select/checkbox types.")
        for opt in options:
            if not isinstance(opt, dict) or 'id' not in opt or 'label' not in opt:
                raise serializers.ValidationError("Each option must have at least 'id' and 'label'.")
        if qtype == 'select':
            if info.get('max_select', 1) != 1:
                raise serializers.ValidationError("For select type, max_select must be 1.")
        if qtype == 'checkbox':
            min_sel = info.get('min_select')
            max_sel = info.get('max_select')
            if max_sel is not None and not isinstance(max_sel, int):
                raise serializers.ValidationError("max_select must be an integer.")
            if min_sel is not None and not isinstance(min_sel, int):
                raise serializers.ValidationError("min_select must be an integer.")
            if (min_sel is not None and max_sel is not None) and min_sel > max_sel:
                raise serializers.ValidationError("min_select cannot be greater than max_select.")
    else:  # text
        min_len = info.get('min_length')
        max_len = info.get('max_length')
        if (isinstance(min_len, int) and isinstance(max_len, int)) and min_len > max_len:
            raise serializers.ValidationError("min_length cannot be greater than max_length.")
    return info


# --------------------------------------------
# Form create/update (با inline question)
# --------------------------------------------
class QuestionInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question_text', 'question_info', 'is_required']

    def validate_question_info(self, value):
        return validate_question_info_schema(value)


class FormCreateUpdateSerializer(serializers.ModelSerializer):
    """
    - creator از request پر می‌شود.
    - access_password (plain) اختیاری است و داخل serializer هش می‌شود.
    - ایجاد/ویرایش inline یک سوال (OneToOne) پشتیبانی می‌شود.
    """
    access_password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    question = QuestionInlineSerializer(write_only=True, required=False)

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'category',
            'is_public', 'access_password',
            'created_at', 'updated_at',
            'question',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError("Title cannot be empty.")
        if len(v) > 255:
            raise serializers.ValidationError("Title length must not exceed 255 characters.")
        return v

    def validate_category(self, value: Category):
        if value is None:
            return None
        req = self.context.get('request')
        user = getattr(req, 'user', None)
        if user and not (user.is_staff or user.is_superuser):
            if value.owner_id != user.id:
                raise serializers.ValidationError("This category does not belong to you.")
        return value

    def create(self, validated_data):
        q_data = validated_data.pop('question', None)
        raw_pwd = validated_data.pop('access_password', '') or ''
        req = self.context.get('request')
        user = getattr(req, 'user', None)

        form = Form.objects.create(
            creator=user,
            access_password_hash=(make_password(raw_pwd) if raw_pwd else ''),
            **validated_data
        )

        if q_data:
            Question.objects.create(form=form, **q_data)
        return form

    def update(self, instance, validated_data):
        q_data = validated_data.pop('question', None)
        raw_pwd = validated_data.pop('access_password', None)

        for f, v in validated_data.items():
            setattr(instance, f, v)

        if raw_pwd is not None:
            instance.access_password_hash = make_password(raw_pwd) if raw_pwd else ''
        instance.save()

        if q_data is not None:
            if hasattr(instance, 'question') and instance.question:
                for f, v in q_data.items():
                    setattr(instance.question, f, v)
                instance.question.save()
            else:
                Question.objects.create(form=instance, **q_data)
        return instance


# --------------------------------------------
# Form read
# --------------------------------------------
class QuestionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_info', 'is_required', 'created_at', 'updated_at']


class FormDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    question = QuestionReadSerializer(read_only=True)

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description',
            'category', 'category_name',
            'creator', 'creator_name',
            'is_public',
            'created_at', 'updated_at',
            'question'
        ]


class FormListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'category', 'category_name', 'is_public', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


# --------------------------------------------
# Process detail (برای نمایش)
# --------------------------------------------
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_info', 'is_required']


class FormSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)  # OneToOne
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
# Process build / create
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


# --------------------------------------------
# Process pages: welcome / end (POST-only views use these)
# --------------------------------------------
class ProcessWelcomeSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)
    total_forms = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = ['id', 'title', 'description', 'process_type', 'total_forms']
    
    def get_total_forms(self, obj):
        return obj.forms.count()

    


class ProcessEndSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)
    total_submissions = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = ['id', 'title', 'description', 'total_submissions']
    
    def get_total_submissions(self, obj):
        return obj.response_sessions.filter(status='submitted').count()


# --------------------------------------------
# Submit: request & response serializers
# --------------------------------------------
class SubmitAnswerItemSerializer(serializers.Serializer):
    form_id = serializers.IntegerField()
    answer = serializers.JSONField()

    def validate(self, data):
        form_id = data['form_id']
        answer = data['answer']

        # Check if form and question exist
        try:
            question = Question.objects.get(form_id=form_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError(f"Form #{form_id} has no question defined.")

        # Validate required answers
        if question.is_required and (answer is None or answer == "" or answer == {}):
            raise serializers.ValidationError(f"Answer for required form #{form_id} cannot be empty.")
        return data


class ProcessSubmitRequestSerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True, required=True)

    def validate(self, attrs):
        form_ids = [a['form_id'] for a in attrs['answers']]
        if len(form_ids) != len(set(form_ids)):
            raise serializers.ValidationError("Duplicate form_id in answers.")
        return attrs


class ProcessSubmitResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    message = serializers.CharField()
    saved_answers = serializers.IntegerField()
