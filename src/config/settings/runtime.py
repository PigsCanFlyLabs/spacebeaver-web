# -*- coding: utf-8 -*-
import os


from configurations import Configuration
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .common import Settings


if os.environ.get("SENTRY_ENDPOINT"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_ENDPOINT"),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=os.environ.get("ENVIRONMENT"),
        send_default_pii=True,
    )


class Runtime(Settings, Configuration):
    DIST = True
    DEBUG = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = "SAMEORIGIN"
    USE_X_FORWARDED_HOST = True

    def _get_env_vars(self):
        return [
            "ENVIRONMENT",
            "SECRET_KEY",
            "SSL",
            "DOMAIN",
            "CACHE_NETLOC",
            "DATA_NETLOC",
            "BROKER_NETLOC",
            "STATIC_URL",
            "MEDIA_URL",
            "OUTSIDE_DATA_NETLOC",
            "STRIPE_LIVE_SECRET_KEY",
            "STRIPE_TEST_SECRET_KEY",
            "STRIPE_LIVE_PUBLIC_KEY",
            "STRIPE_TEST_PUBLIC_KEY",
            "DJSTRIPE_WEBHOOK_SECRET",
        ]

    @property
    def CORS_ORIGIN_REGEX_WHITELIST(self):
        proto = f"{self.PROTO}://"
        prefix = rf"{proto}(.*\.)?"
        segment = rf"{self.DOMAIN_URL.replace(proto, prefix)}"
        suffix = self.DOMAIN.split(".")[-1]
        return [rf"^{segment}\.{suffix}$"]

    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

    @property
    def ALLOWED_HOSTS(self):
        return super(Runtime, self).ALLOWED_HOSTS + ["app"]

    @property
    def INSTALLED_APPS(self):
        base_apps = super().INSTALLED_APPS
        base_apps.insert(
            base_apps.index("django.contrib.staticfiles"), "collectfast"
        )
        return base_apps

    COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"

    @property
    def LOGGING(self):
        level = "ERROR"
        return self._update_logging(
            super().LOGGING,
            level=level,
            formater="default",
            handler=["stdout", "stderr"],
        )
