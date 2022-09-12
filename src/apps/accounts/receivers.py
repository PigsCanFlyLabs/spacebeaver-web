from django.dispatch import Signal, receiver


from constance import config
from constance.signals import config_updated
import stripe

from apps.core.consts import STRIPE_PLAN_PERIOD


DATA_FIELDS = ("TITLE", "DESCRIPTION", "IMAGE", "IMAGE_URL", "PERIOD", "PRICE")
PRICES_FIELDS = ("STRIPE_PRICE_ID", "STRIPE_PRODUCT_ID")


@receiver(config_updated)
def product_management(sender, key, old_value, new_value, **kwargs):
    if key in DATA_FIELDS:
        recurring = {}
        if not sender.STRIPE_PRODUCT_ID:

            stripe_product = stripe.Product.create(
                name=sender.TITLE,
                description=sender.DESCRIPTION,
            )
            sender.STRIPE_PRODUCT_ID = stripe_product.id
            if sender.PERIOD != STRIPE_PLAN_PERIOD.ONETIME.value:
                recurring = {"recurring": {"interval": sender.PERIOD}}
            stripe_price = stripe.Price.create(
                currency="usd",
                unit_amount=sender.PRICE * 100,
                product=stripe_product.id,
                **recurring,
            )
            sender.STRIPE_PRICE_ID = stripe_price.id
        else:
            stripe.Product.modify(
                sid=config.STRIPE_PRODUCT_ID,
                name=sender.TITLE,
                description=sender.DESCRIPTION,
            )
            if sender.PERIOD != STRIPE_PLAN_PERIOD.ONETIME.value:
                recurring = {"recurring": {"interval": sender.PERIOD}}
            stripe_price = stripe.Price.create(
                currency="usd",
                unit_amount=sender.PRICE * 100,
                product=config.STRIPE_PRODUCT_ID,
                **recurring,
            )
            sender.STRIPE_PRICE_ID = stripe_price.id
