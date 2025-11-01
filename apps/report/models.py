# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.core.validators import MinValueValidator, MaxValueValidator
#
#
# class Report(models.Model):
#     class ReportType(models.TextChoices):
#         SUMMARY = "SUMMARY", "Summary"
#         DETAILED = "DETAILED", "Detailed"
#         CUSTOM = "CUSTOM", "Custom"
#         # add your own types as needed
#
#
#     form = models.ForeignKey(
#         "forms.Form",
#         on_delete=models.CASCADE,
#         related_name="reports",
#         db_index=True,
#     )
#
#     generated_at = models.DateTimeField(
#         default=timezone.now,  # or auto_now_add=True if always “created time”
#         editable=False,
#         db_index=True,
#     )
#
#     report_type = models.CharField(
#         max_length=50,
#         choices=ReportType.choices,
#         default=ReportType.SUMMARY,
#     )
#
#     total_sessions_started = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#     )
#     total_sessions_submitted = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#     )
#
#     response_rate = models.DecimalField(
#         max_digits=5,  # e.g., 100.00
#         decimal_places=2,
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         help_text="Percentage in [0, 100].",
#     )
#
#     participants_count = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#     )
#
#     total_answers = models.BigIntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#     )
#
#     data = models.JSONField(
#         default=dict,
#         blank=True,
#         help_text="Computed payload for the report (aggregates, charts, etc.).",
#     )
#
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="created_reports",
#     )
#
#     note = models.TextField(blank=True, default="")
#
#     class Meta:
#         db_table = "reports"
#         indexes = [
#             models.Index(fields=["form", "report_type", "generated_at"]),
#         ]
#         ordering = ["-generated_at"]
#
#     def __str__(self) -> str:
#         return f"Report#{self.pk} [{self.report_type}] for form {self.form_id} @ {self.generated_at:%Y-%m-%d %H:%M}"
from django.db import models
from django.utils import timezone


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('summary', 'Summary'),
        ('detailed', 'Detailed'),
        ('custom', 'Custom'),
    ]

    process = models.ForeignKey(
        'form.Process',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # generated_at = models.DateTimeField(default=timezone.now)
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        default='summary'
    )

    # total_sessions_started = models.PositiveIntegerField(default=0)
    # total_sessions_submitted = models.PositiveIntegerField(default=0)
    # response_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # participants_count = models.PositiveIntegerField(default=0)
    # total_answers = models.BigIntegerField(default=0)


    # core report data (JSON result of analytics)
    data = models.JSONField(default=dict)
    note = models.TextField(null=True, blank=True)

    genearted_at = models.DateTimeField(default=timezone.now)

    created_by = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports_created'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        title = self.title or f"{self.report_type.capitalize()} Report"
        return f"{title} for {self.process.name}"

    def compute_summary(self):
        """
        Optionally compute or format data before saving.
        Called from the ReportCreateAPIView.
        """
        data = self.data or {}
        data['computed_at'] = timezone.now().isoformat()
        return data


