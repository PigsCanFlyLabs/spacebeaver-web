import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from constance import config


@csrf_exempt
def update_product_webhook(request):
    data = json.loads(request.body.decode("utf-8"))
    event_type = data.get("type", "")
    if event_type == "product.created":
        product_id = data.get("data", {}).get("object", {}).get("id", "")
        if product_id:
            config.STRIPE_PRODUCT_ID = product_id

    elif event_type == "price.created":
        price_id = data.get("data", {}).get("object", {}).get("id", "")
        if price_id:
            config.STRIPE_PRICE_ID = price_id

    return HttpResponse(status=200)
