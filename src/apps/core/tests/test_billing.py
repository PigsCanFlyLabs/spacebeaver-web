import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from djstripe.models import Account

from apps.utils.stripe import (
    STRIPE_PUBLIC_API_KEY,
    add_customer_payment_method,
    create_customer,
    create_subscription,
    set_default_payment_method_for_customer,
)


user_model = get_user_model()

user_data = {
    "email": "softformanse@gmail.com",
    "full_name": "softformanse test",
    "password": "testpwd",
}

FIXTURE_DIR_PATH = Path(__file__).parent.joinpath("fixtures")


def load_fixture(filename):
    with FIXTURE_DIR_PATH.joinpath(filename).open("r") as f:
        return json.load(f)


#
# class TestBilling(TestCase):
#     def setUp(self) -> None:
#         self.user = user_model.objects.create(
#             full_name=user_data["full_name"],
#             email=user_data["email"],
#         )
#         self.user.is_active = True
#         self.user.set_password(user_data["password"])
#         self.user.save()
#         FAKE_STANDARD_ACCOUNT = dict(
#             load_fixture("account_standard_acct_1Fg9jUA3kq9o1aTc.json")
#         )
#
#
#     def test_subscription(self):
#         pass
