import logging
from django.core.mail import send_mail
from django.conf import settings

log = logging.getLogger(__name__)

def send_otp_email(to_email: str, code: str):
    subject = "Your verification code"
    message = f"Your verification code is: {code}\nThis code expires in 2 minutes."
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception as e:
        # In dev this should never blow up; in prod log and continue (best-effort)
        log.exception("Failed to send OTP email to %s: %s", to_email, e)