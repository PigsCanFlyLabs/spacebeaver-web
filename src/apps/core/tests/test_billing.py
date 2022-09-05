from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from djstripe.models import Account, Customer

from apps.utils.stripe import (
    STRIPE_PUBLIC_API_KEY,
    add_customer_payment_method,
    create_customer,
    create_subscription,
    delete_subscription,
    detach_payment_method,
    set_default_payment_method_for_customer,
)


STRIPE_PRICE_ID = "1234567"

user_model = get_user_model()

USERDATA = {
    "email": "softformanse@gmail.com",
    "full_name": "softformanse test",
    "password": "testpwd",
}

FIXTURE_DIR_PATH = Path(__file__).parent.joinpath("fixtures")


def load_fixture(filename):
    with FIXTURE_DIR_PATH.joinpath(filename).open("r") as f:
        return json.load(f)


FAKE_PAYMENT_METHOD_I = load_fixture(
    "payment_method_pm_fakefakefakefake0001.json"
)


def update_payment_method(data):
    res = deepcopy(data)
    res["customer"] = "cus_6lsBvm5rJ0zyHc"
    return res


def update_default_payment_method(data):
    res = deepcopy(data)
    res["invoice_settings"]["default_payment_method"] = FAKE_PAYMENT_METHOD_I[
        "id"
    ]
    return res


CUSTOMER_DATA = load_fixture("customer_cus_6lsBvm5rJ0zyHc.json")
SUBSCRIPTION_DATA = load_fixture(
    "subscription_sub_fakefakefakefakefake0001.json"
)


class BaseBillingTestCase(TestCase):
    def setUp(self) -> None:
        self.user = user_model.objects.create(
            full_name=USERDATA["full_name"],
            email=USERDATA["email"],
        )
        self.user.is_active = True
        self.user.set_password(USERDATA["password"])
        self.user.save()

        Customer.sync_from_stripe_data(CUSTOMER_DATA)
        self.customer = Customer.objects.filter(id=CUSTOMER_DATA["id"]).first()


class SubscriptionTestCase(BaseBillingTestCase):
    def test_customer_creation(self):
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(self.user.customer_id, "cus_6lsBvm5rJ0zyHc")

    @patch(
        "stripe.PaymentMethod._cls_attach",
        return_value=update_payment_method(CUSTOMER_DATA),
        autospec=True,
    )
    @patch(
        "stripe.Customer.modify",
        return_value=update_default_payment_method(CUSTOMER_DATA),
        autospec=True,
    )
    @patch(
        "stripe.Subscription.create",
        return_value=deepcopy(SUBSCRIPTION_DATA),
        autospec=True,
    )
    @patch(
        "stripe.Subscription.delete",
        return_value=None,
        autospec=True,
    )
    def test_create_subscription(
        self, attach_mock, modify_mock, subscription_mock, delete_mock
    ):
        # CREATE SUBSCRIPTION FLOW
        # See core/view/subscriptions.py  CreateSubscriptionAPIView.post

        payment_method = add_customer_payment_method(
            FAKE_PAYMENT_METHOD_I["id"], self.user.customer_id
        )

        self.assertEqual(payment_method["customer"], self.user.customer_id)

        customer = set_default_payment_method_for_customer(
            FAKE_PAYMENT_METHOD_I["id"], self.user.customer_id
        )

        self.assertEqual(
            customer["invoice_settings"]["default_payment_method"],
            FAKE_PAYMENT_METHOD_I["id"],
        )
        subscription = create_subscription(STRIPE_PRICE_ID, customer["id"])

        self.assertEqual(subscription["id"], SUBSCRIPTION_DATA["id"])
        self.assertEqual(
            subscription["items"]["data"][0]["price"],
            SUBSCRIPTION_DATA["items"]["data"][0]["price"],
        )
        # CANCEL SUBSCRIPTION FLOW
        # See core/view/billing.py  CancelSubscriptionAPIView.post

        self.assertEqual(delete_subscription(subscription["id"]), None)


class PaymentMethod(BaseBillingTestCase):
    @patch(
        "stripe.PaymentMethod._cls_attach",
        return_value=update_payment_method(CUSTOMER_DATA),
        autospec=True,
    )
    @patch(
        "stripe.Customer.modify",
        return_value=update_default_payment_method(CUSTOMER_DATA),
        autospec=True,
    )
    @patch(
        "stripe.Subscription.create",
        return_value=deepcopy(SUBSCRIPTION_DATA),
        autospec=True,
    )
    @patch(
        "stripe.PaymentMethod.detach",
        return_value=None,
        autospec=True,
    )
    def test_update_payment_method(
        self, attach_mock, modify_mock, subscription_mock, detach_mock
    ):
        # UPDATE/DELETE PAYMENT METHOD FLOW
        # See core/view/billing.py  UpdatePaymentMethodAPIView.post
        # See core/view/billing.py  DeletePaymentMethodAPIView.post

        self.assertEqual(self.customer.default_payment_method, None)

        payment_method = add_customer_payment_method(
            FAKE_PAYMENT_METHOD_I["id"], self.user.customer_id
        )
        self.assertEqual(payment_method["customer"], self.user.customer_id)
        customer = set_default_payment_method_for_customer(
            FAKE_PAYMENT_METHOD_I["id"], self.user.customer_id
        )
        self.assertEqual(
            customer["invoice_settings"]["default_payment_method"],
            FAKE_PAYMENT_METHOD_I["id"],
        )

        self.assertIsNone(detach_payment_method(payment_method["id"]))
