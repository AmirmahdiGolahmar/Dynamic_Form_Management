from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # If the Authorization header exists, keep default behavior
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        # Otherwise read from cookie
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None  # no cookie → let other authenticators try

        try:
            validated = self.get_validated_token(raw_token)
        except InvalidToken as e:
            raise AuthenticationFailed("Invalid access token") from e

        user = self.get_user(validated)
        return (user, validated)  # <-- tuple is crucial
