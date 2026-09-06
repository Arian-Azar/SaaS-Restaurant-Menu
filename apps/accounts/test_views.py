from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.restaurants.models import Restaurant

User = get_user_model()


class RegisterViewTests(TestCase):
    """تست کامل جریان ثبت‌نام از طریق HTTP (نه صدا زدن مستقیم سرویس)."""

    def setUp(self):
        self.url = reverse('register')
        self.valid_data = {
            'restaurant_name': 'کافه آریان',
            'full_name': 'آرین محمدی',
            'username': 'arian_owner',
            'email': 'arian@example.com',
            'phone_number': '09120000000',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }

    def test_get_register_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_successful_registration_creates_user_restaurant_and_logs_in(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='arian_owner').exists())
        self.assertTrue(Restaurant.objects.filter(name='کافه آریان').exists())

        # کاربر باید بلافاصله بعد از ثبت‌نام لاگین باشد (بدون نیاز به ورود دستی مجدد).
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'کافه آریان')

    def test_duplicate_username_is_rejected_and_nothing_is_created(self):
        User.objects.create_user(username='arian_owner', password='pass12345')

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 200)  # همان صفحه فرم با خطا برگردانده می‌شود
        self.assertContains(response, 'قبلاً استفاده شده')
        # هیچ رستوران جدیدی نباید ساخته شده باشد.
        self.assertFalse(Restaurant.objects.filter(name='کافه آریان').exists())

    def test_password_mismatch_is_rejected(self):
        data = {**self.valid_data, 'password_confirm': 'ChiziDigar123!'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'یکسان نیستند')
        self.assertFalse(User.objects.filter(username='arian_owner').exists())


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner1', password='StrongPass123!')
        self.restaurant = Restaurant.objects.create(owner=self.owner, name='رستوران تست')

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'), {'username': 'owner1', 'password': 'StrongPass123!'}
        )
        self.assertRedirects(response, reverse('dashboard'))

    def test_wrong_password_shows_error_and_does_not_login(self):
        response = self.client.post(
            reverse('login'), {'username': 'owner1', 'password': 'wrong-password'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('dashboard')}"
        )

    def test_logout_then_dashboard_redirects_to_login(self):
        self.client.login(username='owner1', password='StrongPass123!')
        self.client.post(reverse('logout'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
