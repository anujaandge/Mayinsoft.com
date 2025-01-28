import logging
import time
from django.contrib.auth import authenticate, login

logger = logging.getLogger('django')

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request
        logger.info(f"Request: {request.method} {request.path}")

        response = self.get_response(request)

        # Log the response
        logger.info(f"Response: {response.status_code} {response.reason_phrase}")

        return response

class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        logger.info(f"Request: {request.method} {request.path} took {duration:.2f} seconds")
        return response

class AuthenticationMiddleware:
    """
    Middleware to authenticate users based on custom logic.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            user = authenticate(request)
            if user is not None:
                login(request, user)
                logger.info(f"User {user.username} authenticated successfully")
            else:
                logger.warning("Authentication failed")
        return self.get_response(request)
