from django.db import models
import uuid
from django.conf import settings

# Create your models here.



class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProcessForm(models.Model):
    process = models.ForeignKey(to='Process', on_delete=models.CASCADE)
    form = models.ForeignKey(to='Form', on_delete=models.CASCADE)
    order_index = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['process', 'form'], name='unique_process_form')
        ]
        ordering = ['order_index']

    def __str__(self):
        return f"{self.process.name} → {self.form.title}"



class Form(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='processes')
    category = models.ForeignKey(
        to='Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='forms',
        )
    is_public = models.BooleanField(default=False)
    access_password_hash = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Process(models.Model):
    PROCESS_TYPE_CHOICES = [
        ('linear', 'Linear'),
        ('free', 'Free'),
    ]
    forms = models.ManyToManyField(to='Form', through='ProcessForm', related_name='processes')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='processes')
    category = models.ForeignKey(
        to='Category', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='processes',
        )
    is_public = models.BooleanField(default=False)
    access_password_hash = models.CharField(max_length=128, blank=True, null=True)
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPE_CHOICES, default='linear')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Question(models.Model):
    form = models.OneToOneField(
        to='Form',
        on_delete=models.CASCADE,
        related_name='question',
    )
    question_text = models.TextField()
    question_info = models.JSONField() # type, options, etc.
    is_required = models.BooleanField(default=False)
    order_index = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text
    


class ResponseSession(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('abandoned', 'Abandoned'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process = models.ForeignKey(to='Process', on_delete=models.CASCADE, related_name='response_sessions')
    responder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='response_sessions',
        )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"Session {self.id} ({self.status})"


class Answer(models.Model):
    response_session = models.ForeignKey(
        to='ResponseSession', 
        on_delete=models.CASCADE,
        related_name='answers',
        )
    form = models.ForeignKey(
        to='Form', 
        on_delete=models.CASCADE,
        related_name='answers',
        )
    question = models.ForeignKey(
        to='Question', 
        on_delete=models.CASCADE,
        related_name='answers',
        )
    answer_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer {self.id} to Q{self.question.id}"


