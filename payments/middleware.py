from django.conf import settings


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY
        response["Referrer-Policy"] = "same-origin"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
