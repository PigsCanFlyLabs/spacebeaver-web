from datetime import datetime

from django import conf
from django.contrib import admin
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import normalize_newlines


from constance import LazyConfig, settings
from constance.admin import ConstanceAdmin, ConstanceForm
import stripe

# Register your models here.
from apps.core.consts import STRIPE_PLAN_PERIOD
from apps.core.models import BlockedNumber, Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "used",
        "external_phone",
        "external_email",
    )


@admin.register(BlockedNumber)
class BlockedNumbersAdmin(admin.ModelAdmin):
    list_display = ("number",)


config = LazyConfig()

DATA_FIELDS = ("TITLE", "DESCRIPTION", "IMAGE", "IMAGE_URL", "PERIOD", "PRICE")
PRICES_FIELDS = ("STRIPE_PRICE_ID", "STRIPE_PRODUCT_ID")


class CustomConstanceForm(ConstanceForm):
    def save(self):
        for file_field in self.files:
            file = self.cleaned_data[file_field]
            self.cleaned_data[file_field] = default_storage.save(
                file.name, file
            )
        old_values = {}
        new_values = {}
        for name in settings.CONFIG:
            current = getattr(config, name)
            new = self.cleaned_data[name]

            old_values.update({name: current})
            new_values.update({name: new})
            if isinstance(new, str):
                new = normalize_newlines(new)

            if (
                conf.settings.USE_TZ
                and isinstance(current, datetime)
                and not timezone.is_aware(current)
            ):
                current = timezone.make_aware(current)

            if current != new:
                setattr(config, name, new)

        if (
            not new_values["STRIPE_PRODUCT_ID"]
            and not old_values["STRIPE_PRODUCT_ID"]
        ):
            try:
                stripe_product = stripe.Product.create(
                    name=new_values["TITLE"],
                    description=new_values["DESCRIPTION"],
                )
                setattr(config, "STRIPE_PRODUCT_ID", stripe_product.id)
            except Exception as e:
                setattr(
                    config,
                    "STRIPE_PRODUCT_ID",
                    "PRODUCT NOT CREATED \n" + str(e),
                )

            try:
                recurring = {}
                if config.PERIOD != STRIPE_PLAN_PERIOD.ONETIME.value:
                    recurring = {"recurring": {"interval": config.PERIOD}}
                stripe_price = stripe.Price.create(
                    currency="usd",
                    unit_amount=config.PRICE * 100,
                    product=config.STRIPE_PRODUCT_ID,
                    **recurring,
                )
                setattr(config, "STRIPE_PRICE_ID", stripe_price.id)
            except Exception as e:
                setattr(
                    config, "STRIPE_PRICE_ID", "PRICE NOT CREATED \n" + str(e)
                )
        elif (
            new_values["STRIPE_PRODUCT_ID"]
            and new_values["STRIPE_PRODUCT_ID"]
            == old_values["STRIPE_PRODUCT_ID"]
            and (
                old_values["PRICE"] != new_values["PRICE"]
                or old_values["PERIOD"] != new_values["PERIOD"]
            )
        ):

            try:
                recurring = {}

                if config.PERIOD != STRIPE_PLAN_PERIOD.ONETIME.value:
                    recurring = {"recurring": {"interval": config.PERIOD}}
                stripe_price = stripe.Price.create(
                    currency="usd",
                    unit_amount=config.PRICE * 100,
                    product=config.STRIPE_PRODUCT_ID,
                    **recurring,
                )
                setattr(config, "STRIPE_PRICE_ID", stripe_price.id)
            except Exception as e:
                setattr(
                    config, "STRIPE_PRICE_ID", "PRICE NOT CREATED \n" + str(e)
                )
        elif (
            old_values["STRIPE_PRODUCT_ID"]
            and not new_values["STRIPE_PRODUCT_ID"]
            and old_values["STRIPE_PRICE_ID"]
        ):
            setattr(config, "STRIPE_PRICE_ID", "")


ConstanceAdmin.change_list_form = CustomConstanceForm
