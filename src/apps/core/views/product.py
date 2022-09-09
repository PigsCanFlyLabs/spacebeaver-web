import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from constance import config


@csrf_exempt
def update_product_webhook(request):
    data = json.loads(request.body.decode("utf-8"))
    event_type = data.get("type", "")
    default_price_id = (
        data.get("data", {}).get("object", {}).get("default_price", "")
    )
    if (
        event_type == "product.updated"
        and default_price_id == config.STRIPE_PRICE_ID
    ):
        product_name = data.get("data", {}).get("object", {}).get("name", "")
        product_description = (
            data.get("data", {}).get("object", {}).get("description", "")
        )
        product_images = (
            data.get("data", {}).get("object", {}).get("images", [])
        )
        image_url = product_images[0] if len(product_images) > 0 else ""
        config.TITLE = product_name
        config.DESCRIPTION = product_description
        config.IMAGE_URL = image_url

    elif event_type == "price.updated":
        price_id = data.get("data", {}).get("object", {}).get("id", "")
        if price_id == config.STRIPE_PRICE_ID:
            config.PRICE = int(
                int(
                    data.get("data", {})
                    .get("object", {})
                    .get("unit_amount", 100)
                )
                / 100
            )

    return HttpResponse(status=200)
