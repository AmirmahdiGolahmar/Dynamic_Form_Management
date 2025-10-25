import random
import re
from django.core.cache import cache

OTP_TTL = 120            # seconds
OTP_COOLDOWN = 60        # seconds
OTP_MAX_ATTEMPTS = 5

def normalize_email(email: str) -> str:
    email = (email or "").strip().lower()
    return email

def generate_otp(n=6) -> str:
    return "".join(random.choice("0123456789") for _ in range(n))

def otp_key(email: str) -> str:
    return f"otp:email:{email}"

def otp_cooldown_key(email: str) -> str:
    return f"otp:cooldown:email:{email}"

def put_otp(email: str, code: str):
    cache.set(otp_key(email), {"code": code, "attempts": 0}, OTP_TTL)

def get_otp(email: str):
    return cache.get(otp_key(email))

def clear_otp(email: str):
    cache.delete(otp_key(email))

def bump_attempt(email: str) -> int:
    data = cache.get(otp_key(email))
    if not data:
        return 0
    data["attempts"] += 1
    cache.set(otp_key(email), data, OTP_TTL)
    return data["attempts"]

def set_cooldown(email: str):
    cache.set(otp_cooldown_key(email), True, OTP_COOLDOWN)

def in_cooldown(email: str) -> bool:
    return cache.get(otp_cooldown_key(email)) is not Nones