from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "process",
        "report_type",
        "generated_at",
        "total_sessions_started",
        "total_sessions_submitted",
        "response_rate",
        "participants_count",
        "created_by",
    )
    list_filter = (
        "report_type",
        "generated_at",
        "process__category",
    )
    search_fields = (
        "process__name",
        "created_by__username",
        "note",
    )
    readonly_fields = (
        "generated_at",
        "total_sessions_started",
        "total_sessions_submitted",
        "response_rate",
        "participants_count",
        "total_answers",
        "data",
    )
    fieldsets = (
        ("Report Info", {
            "fields": ("process", "report_type", "generated_at", "created_by"),
        }),
        ("Statistics", {
            "fields": (
                "total_sessions_started",
                "total_sessions_submitted",
                "response_rate",
                "participants_count",
                "total_answers",
            ),
        }),
        ("Data & Notes", {
            "fields": ("data", "note"),
        }),
    )

    ordering = ("-generated_at",)
    date_hierarchy = "generated_at"
