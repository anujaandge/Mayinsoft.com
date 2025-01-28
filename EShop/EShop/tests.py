from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from .middleware import LoggingMiddleware, PerformanceMonitoringMiddleware, AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser, User

class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_logging_middleware(self):
        request = self.factory.get('/')
        response = HttpResponse()
        middleware = LoggingMiddleware(lambda req: response)
        middleware(request)
        # Check the log file or console for the expected log entries

    def test_performance_monitoring_middleware(self):
        request = self.factory.get('/')
        response = HttpResponse()
        middleware = PerformanceMonitoringMiddleware(lambda req: response)
        middleware(request)
        # Check the log file or console for the expected log entries

    def test_authentication_middleware(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        response = HttpResponse()
        middleware = AuthenticationMiddleware(lambda req: response)
        middleware(request)
        # Check if the user is authenticated correctly
        self.assertTrue(request.user.is_authenticated)
