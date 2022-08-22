from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from django_countries.fields import Country

from apps.core.models import BlockedNumber


user_model = get_user_model()
user_data = {
    "setUp": {
        "email": "softformanse@gmail.com",
        "full_name": "softformanse test",
        "password": "testpwd",
    },
    "creation_test": {
        "email": "softformanse1@gmail.com",
        "full_name": "softformanse1 test",
        "password": "testpwd1",
    },
}

update_data = [
    {
        "company": "SOFTFORMANCE",
        "company_email": "softformance@gmail.com",
        "twillion_number": "+380965589631",
    },
    {
        "company": "SOFTFORMANCE2",
        "company_email": "softformance@gmail1.com",
        "twillion_number": "+380965533631",
    },
]


class UserTestCase(TestCase):

    BLOCKED_NUMBER = "+380996587932"

    def create_runtime_user(self):
        user = user_model.objects.create(
            full_name=user_data["creation_test"]["full_name"],
            email=user_data["creation_test"]["password"],
            country=Country("UA"),
            **update_data[0],
        )

        user.is_active = True
        user.set_password(user_data["creation_test"]["password"])
        user.save()
        return user

    def setUp(self) -> None:
        self.user = user_model.objects.create(
            full_name=user_data["setUp"]["full_name"],
            email=user_data["setUp"]["email"],
        )
        self.user.is_active = True
        self.user.set_password(user_data["setUp"]["password"])
        self.user.save()

    def test_user_creation(self):
        user = self.create_runtime_user()
        self.assertEqual(user_model.objects.count(), 2)

        self.assertTrue(user.is_active)
        self.assertEqual(user.country.code, "UA")

        for field, value in update_data[0].items():
            self.assertEqual(getattr(user, field), value)

        self.assertEqual(user.customer_subscription, None)
        self.assertFalse(user.dont_have_active_subscriptions)
        self.assertFalse(user.have_any_subscription)

        user.delete()
        self.assertEqual(user_model.objects.count(), 1)

    def test_login_user(self):
        c = Client()
        login_result = c.login(
            username=user_data["setUp"]["email"],
            password=user_data["setUp"]["password"],
        )
        self.assertTrue(login_result)

    def test_update_user_info(self):
        user_model.objects.filter(pk=self.user.pk).update(
            country=Country("UK"), **update_data[1]
        )

        user = user_model.objects.get(pk=self.user.pk)
        for field, value in update_data[1].items():
            self.assertEqual(getattr(user, field), value)
        self.assertEqual(user.country.code, "UK")

    def test_blocked_numbers(self):
        user_blocked_numbers_cnt = (
            BlockedNumber.object.get_user_blocked_numbers(self.user).count()
        )

        self.assertEqual(user_blocked_numbers_cnt, 0)

        BlockedNumber.object.add_user_blocked_number(
            number=self.BLOCKED_NUMBER, user=self.user
        )
        # Test adding identical numbers
        BlockedNumber.object.add_user_blocked_number(
            number=self.BLOCKED_NUMBER, user=self.user
        )

        user_blocked_numbers = BlockedNumber.object.get_user_blocked_numbers(
            self.user
        )

        self.assertEqual(user_blocked_numbers.count(), 1)

        user_blocked_number = user_blocked_numbers.first()

        self.assertEqual(user_blocked_number.number, self.BLOCKED_NUMBER)

        BlockedNumber.object.delete_user_blocked_number(
            user_blocked_number.id, self.user
        )

        self.assertEqual(
            BlockedNumber.object.filter(user=self.user).count(), 0
        )

        for i in range(5):
            BlockedNumber.object.add_user_blocked_number(
                number=self.BLOCKED_NUMBER.replace("5", str(i)), user=self.user
            )

        self.assertEqual(
            BlockedNumber.object.filter(user=self.user).count(), 5
        )
