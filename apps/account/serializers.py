# accounts/serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import (
    normalize_email, generate_otp, put_otp, get_otp, clear_otp,
    set_cooldown, in_cooldown, bump_attempt, OTP_MAX_ATTEMPTS
)
from .emailer import send_otp_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "password", "email", "phone", "gender", "address")
        extra_kwargs = {
            "email": {"required": False, "allow_null": True, "allow_blank": True},
            "phone": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone", "gender", "address", "updated_at")


class LoginSerializer(TokenObtainPairSerializer):
    """
    Accepts either:
      - username + password
      - phone + password
      - identifier + password  (identifier can be username or phone)
    """
    identifier = serializers.CharField(required=False)

    def validate(self, attrs):
        identifier = attrs.pop("identifier", None)
        username = attrs.get("username")

        # Unify: if identifier provided, resolve to username
        if identifier and not username:
            # Try phone, then username
            user_qs = User.objects.filter(phone=identifier)
            if not user_qs.exists():
                user_qs = User.objects.filter(username=identifier)
            if user_qs.exists():
                attrs["username"] = user_qs.first().username
            else:
                # keep username as-is; let parent raise invalid creds
                attrs["username"] = identifier

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["phone"] = user.phone
        return token


class TokenPairSerializer(TokenObtainPairSerializer):
    """
    Accepts:
      {"username": "...", "password": "..."}  OR
      {"identifier": "0912... | +98912... | username", "password": "..."}
    """
    def validate(self, attrs):
        identifier = self.initial_data.get("identifier")
        if identifier and not self.initial_data.get("username"):
            # resolve identifier -> username if it's a phone or already a username
            user = User.objects.filter(phone=identifier).first() or \
                   User.objects.filter(username=identifier).first()
            # If found, set username for parent validation; otherwise let it fail normally
            attrs["username"] = user.username if user else identifier
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # optional custom claims
        token["username"] = user.username
        token["phone"] = user.phone
        return token


class EmailOTPRequestSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate_email(self, v):
        email = normalize_email(v)
        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email address.")
        return email

    def create(self, validated_data):
        email = validated_data["email"]
        if in_cooldown(email):
            raise serializers.ValidationError("OTP recently sent. Please wait before requesting again.")

        code = generate_otp(6)
        put_otp(email, code)
        set_cooldown(email)
        send_otp_email(email, code)

        payload = {"sent": True}
        if getattr(settings, "DEBUG_SHOW_OTP", False):
            payload["debug_code"] = code
        return payload


class EmailOTPVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    code  = serializers.CharField()

    def validate(self, attrs):
        email = normalize_email(attrs.get("email"))
        code  = (attrs.get("code") or "").strip()

        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError({"email": "Invalid email address."})

        data = get_otp(email)
        if not data:
            raise serializers.ValidationError({"code": "Code expired or not requested."})

        if data.get("attempts", 0) >= OTP_MAX_ATTEMPTS:
            raise serializers.ValidationError({"code": "Too many attempts. Request a new code."})

        if data["code"] != code:
            attempts = bump_attempt(email)
            raise serializers.ValidationError({"code": f"Invalid code ({attempts}/{OTP_MAX_ATTEMPTS})."})

        attrs["email"] = email
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]

        existing = list(User.objects.filter(email__iexact=email)[:2])
        if len(existing) > 1:
            raise serializers.ValidationError(
                {"email": "Multiple accounts use this email. Contact support."}
            )

        if not existing:
            raise serializers.ValidationError(
                {"email": "No account found with this email address."}
            )

        # If user exists, continue as before
        user = existing[0]

        # success → clear OTP
        clear_otp(email)

        # issue JWT pair
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        access = refresh.access_token
        access["email"] = user.email

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "refresh": str(refresh),
            "access": str(access),
        }