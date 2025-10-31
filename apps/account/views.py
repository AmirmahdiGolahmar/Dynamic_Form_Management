from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, MeSerializer, LoginSerializer, TokenPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import EmailOTPRequestSerializer, EmailOTPVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"message": "Registered successfully."}, status=status.HTTP_201_CREATED)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Extract tokens returned by SimpleJWT
        access = response.data.get("access")
        refresh = response.data.get("refresh")

        # Clear tokens from response JSON if you want cookie-only auth
        response.data.pop("access", None)
        response.data.pop("refresh", None)

        # Optional: lifespan
        access_lifetime = api_settings.ACCESS_TOKEN_LIFETIME or timedelta(minutes=5)
        refresh_lifetime = api_settings.REFRESH_TOKEN_LIFETIME or timedelta(days=1)

        # Set cookies — HttpOnly makes JS unable to steal them
        response.set_cookie(
            key="access_token",
            value=access,
            max_age=int(access_lifetime.total_seconds()),
            httponly=True,
            secure=True,            # True in production (HTTPS)
            samesite="None",         # None for cross-site (SPA on another domain)
            path="/"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            max_age=int(refresh_lifetime.total_seconds()),
            httponly=True,
            secure=True,
            samesite="None",
            path="/"
        )

        return response

class RefreshView(TokenRefreshView):
    pass

class TokenPairView(TokenObtainPairView):
    serializer_class = TokenPairSerializer

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)

    def patch(self, request):
        ser = MeSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

class EmailOTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmailOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.save()
        return Response({"data" : data, "hhhhhhhhhhhhhhhhhhhhhhi" : 1}, status=status.HTTP_200_OK)

class EmailOTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmailOTPVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)

