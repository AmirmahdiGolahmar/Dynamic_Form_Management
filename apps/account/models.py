from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class User(AbstractUser):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]

    phone_regex = RegexValidator(
        regex=r'^(?:\+98|0)?9\d{9}$',
        message="Phone must start with 09… (09123456789) or +98… (+989123456789).",
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=13,
        unique=True,
        blank=True,
        null=True,
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or (self.phone or "User")
