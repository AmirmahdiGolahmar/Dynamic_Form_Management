# # app/models.py
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
