"""
Middleware to avoid Network Error / 403 for API calls from frontend.
Exempts /api/ from CSRF so SPA can POST/PUT/DELETE without CSRF token.
"""


class DisableCSRFForAPI:
    """Set csrf_processing_done so CSRF is skipped for /api/ requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            request.csrf_processing_done = True
        return self.get_response(request)
