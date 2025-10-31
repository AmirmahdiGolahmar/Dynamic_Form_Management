from django.contrib import admin
from .models import Category, Form, Process, ProcessForm, Question, ResponseSession, Answer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


class ProcessFormInline(admin.TabularInline):
    model = ProcessForm
    extra = 1
    autocomplete_fields = ('form',)
    ordering = ('order_index',)


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'category', 'process_type', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    list_filter = ('process_type', 'is_public', 'created_at')
    inlines = [ProcessFormInline]
    ordering = ('-created_at',)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    list_filter = ('is_public', 'created_at')
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('form', 'question_text', 'is_required', 'created_at')
    search_fields = ('question_text', 'form__title')
    list_filter = ('is_required',)


@admin.register(ResponseSession)
class ResponseSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'process', 'responder', 'status', 'started_at', 'submitted_at')
    search_fields = ('id', 'process__name', 'responder__username')
    list_filter = ('status', 'started_at')
    ordering = ('-started_at',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'response_session', 'form', 'question', 'created_at')
    search_fields = ('question__question_text', 'form__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
