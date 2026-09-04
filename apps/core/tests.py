from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.restaurants.models import Restaurant

from .middleware import TenantMiddleware
from .tenant import get_current_restaurant

User = get_user_model()


class TenantMiddlewareTests(TestCase):
    """
    تست می‌کند که TenantMiddleware واقعاً رستوران درست را برای کاربر لاگین‌شده
    ست می‌کند، برای Super Admin هیچ رستورانی ست نمی‌کند، و در پایان
    request کانتکست را پاک می‌کند.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.restaurant = Restaurant.objects.create(owner=self.owner, name='رستوران تست')
        self.superadmin = User.objects.create_superuser(
            username='super', password='pass12345', email='super@example.com'
        )

    def _run_middleware_and_capture(self, user):
        captured = {}

        def fake_view(request):
            captured['restaurant'] = get_current_restaurant()
            return HttpResponse('ok')

        middleware = TenantMiddleware(fake_view)
        request = self.factory.get('/')
        request.user = user
        middleware(request)
        return captured['restaurant']

    def test_owner_gets_their_restaurant_set_during_request(self):
        restaurant_during_request = self._run_middleware_and_capture(self.owner)
        self.assertEqual(restaurant_during_request, self.restaurant)

    def test_superadmin_gets_no_restaurant_set(self):
        restaurant_during_request = self._run_middleware_and_capture(self.superadmin)
        self.assertIsNone(restaurant_during_request)

    def test_context_is_cleared_after_request(self):
        self._run_middleware_and_capture(self.owner)
        # بعد از پایان request، کانتکست باید پاک شده باشد.
        self.assertIsNone(get_current_restaurant())
