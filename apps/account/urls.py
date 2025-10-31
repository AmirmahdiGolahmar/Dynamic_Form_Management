from django.urls import path
from .views import RegisterView, LoginView, RefreshView, MeView, TokenPairView
from .views import EmailOTPRequestView, EmailOTPVerifyView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/",    LoginView.as_view(),    name="auth-login"),
    path("refresh/",  RefreshView.as_view(),  name="auth-refresh"),
    path("me/",       MeView.as_view(),       name="auth-me"),
    path("token/", TokenPairView.as_view(), name="token_obtain_pair"),
    path("otp/request/", EmailOTPRequestView.as_view(), name="otp-request"),
    path("otp/verify/", EmailOTPVerifyView.as_view(), name="otp-verify"),
]