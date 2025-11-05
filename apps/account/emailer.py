from account.tasks import send_otp_email_task

def send_otp_email(to_email: str, code: str):
    """
    Schedule OTP email to be sent asynchronously using Celery.
    """
    send_otp_email_task.delay(to_email, code)



