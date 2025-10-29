from rest_framework.throttling import SimpleRateThrottle

class OTPAnonThrottle(SimpleRateThrottle):
    scope = "otp_anon"
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

class OTPEmailThrottle(SimpleRateThrottle):
    scope = "otp_email"
    def get_cache_key(self, request, view):
        email = (request.data.get("email") or request.query_params.get("email") or "").strip().lower()
        if not email:
            return None
        return self.cache_format % {"scope": self.scope, "ident": email}