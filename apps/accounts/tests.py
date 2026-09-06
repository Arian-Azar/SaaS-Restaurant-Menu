from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.restaurants.models import Restaurant

from .services import register_restaurant_owner

User = get_user_model()


class RegisterRestaurantOwnerServiceTests(TestCase):
    """
    تست‌های سرویس apps/accounts/services.py — جدا از HTTP، تا هم سریع‌تر
    اجرا شود و هم مستقیماً روی مهم‌ترین قانون کسب‌وکار این بخش تمرکز کند:
    ساخت User و Restaurant باید اتمیک باشد.
    """

    def test_creates_user_and_linked_restaurant(self):
        user, restaurant = register_restaurant_owner(
            username='arian_owner',
            password='StrongPass123!',
            restaurant_name='کافه آریان',
            email='arian@example.com',
            phone_number='09120000000',
            full_name='آرین محمدی',
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(restaurant.owner, user)
        self.assertEqual(user.role, User.Role.RESTAURANT_OWNER)
        self.assertTrue(user.check_password('StrongPass123!'))
        # اتصال دوطرفه: از طریق related_name هم باید در دسترس باشد.
        self.assertEqual(user.restaurant, restaurant)

    def test_registration_is_atomic_user_rolled_back_if_restaurant_fails(self):
        """
        اگر ساخت Restaurant به هر دلیلی شکست بخورد، User ساخته‌شده هم باید
        Rollback شود — دقیقاً همان چیزی که در پروپوزال به‌عنوان
        فرآیند اتمیک ثبت‌نام توضیح داده شده بود.
        """
        with patch(
            'apps.accounts.services.Restaurant.objects.create',
            side_effect=IntegrityError('شبیه‌سازی خطای دیتابیس'),
        ):
            with self.assertRaises(IntegrityError):
                register_restaurant_owner(
                    username='rollback_user',
                    password='StrongPass123!',
                    restaurant_name='رستوران ناموفق',
                )

        self.assertFalse(User.objects.filter(username='rollback_user').exists())
        self.assertEqual(Restaurant.objects.count(), 0)
