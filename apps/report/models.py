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
    generated_at = models.DateTimeField(default=timezone.now)
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        default='summary'
    )

    total_sessions_started = models.PositiveIntegerField(default=0)
    total_sessions_submitted = models.PositiveIntegerField(default=0)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    participants_count = models.PositiveIntegerField(default=0)
    total_answers = models.BigIntegerField(default=0)

    data = models.JSONField(default=dict)
    note = models.TextField(null=True, blank=True)

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
        return f"Report ({self.report_type}) for {self.process.name}"

    @property
    def submission_rate(self):
        """محاسبه درصد ارسال نسبت به شروع."""
        if self.total_sessions_started == 0:
            return 0
        return round((self.total_sessions_submitted / self.total_sessions_started) * 100, 2)
