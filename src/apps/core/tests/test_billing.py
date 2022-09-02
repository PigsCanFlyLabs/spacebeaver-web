import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from djstripe.models import Account, Customer

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
