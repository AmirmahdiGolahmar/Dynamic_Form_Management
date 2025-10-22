from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, MeSerializer, LoginSerializer, TokenPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import EmailOTPRequestSerializer, EmailOTPVerifySerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"message": "Registered successfully."}, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    """
    POST body can be:
      { "username": "...", "password": "..." }
      { "phone": "0912...", "password": "..." }
      { "identifier": "+98912...", "password": "..." }
    """
    serializer_class = LoginSerializer

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
        return Response(data, status=status.HTTP_200_OK)

class EmailOTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmailOTPVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.save()
        return Response(data, status=status.HTTP_200_OK)

