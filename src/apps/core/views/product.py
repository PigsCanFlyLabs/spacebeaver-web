from constance import config
from djstripe import webhooks


@webhooks.handler("product.updated")
def update_product_webhook(event, **kwargs):
    product_name = event.data.get("name", "")
    description = event.data.get("description", "")
    images = event.data.get("images", [])
    image = ""
    if len(images) > 0:
        image = images[0]

    setattr(config, "TITLE", product_name)
    setattr(config, "DESCRIPTION", description)
    setattr(config, "IMAGE_URL", image)
