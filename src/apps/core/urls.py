from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from apps.core.views import *


app_name = "core"

view_urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path(
        "successful-registration/",
        SuccessfulRegistration.as_view(),
        name="successful-registration",
    ),
    path(
        "personal-info/",
        login_required(PersonalInfoView.as_view()),
        name="personal-info",
    ),
    path(
        "add-device/",
        login_required(AddDeviceView.as_view()),
        name="add-device",
    ),
    path(
        "pick-plan/", login_required(PickPlanView.as_view()), name="pick-plan"
    ),
    path(
        "payment-success",
        login_required(PaymentSuccessView.as_view()),
        name="payment-success",
    ),
    path("login", LoginView.as_view(), name="login"),
    path(
        "replace-device",
        login_required(ReplaceDeviceView.as_view()),
        name="replace-device",
    ),
    path(
        "dashboard", login_required(DashboardView.as_view()), name="dashboard"
    ),
    path(
        "subscription",
        login_required(SubscriptionView.as_view()),
        name="subscription",
    ),
    path("billing", login_required(BillingView.as_view()), name="billing"),
    path(
        "blocked-numbers/",
        login_required(BlockedNumbersView.as_view()),
        name="blocked-numbers",
    ),
    path(
        "delete-blocked-number/<int:pk>",
        login_required(DeleteBlockedNumberView.as_view()),
        name="delete-blocked-number",
    ),
    path(
        "success-new-password/",
        auth_view.PasswordResetDoneView.as_view(
            template_name="success_chane_pass.html"
        ),
        name="success-new-password",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_view.PasswordResetConfirmView.as_view(
            template_name="new_password.html",
            success_url=reverse_lazy("core:success-new-password"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "new-password-link/",
        auth_view.PasswordResetDoneView.as_view(
            template_name="password_link.html"
        ),
        name="new-password-link",
    ),
    path(
        "update-plan/",
        login_required(UpdatePlanView.as_view()),
        name="update-plan",
    ),
    path(
        "forget-password/",
        auth_view.PasswordResetView.as_view(
            template_name="forget_password.html",
            email_template_name="password_reset_email.txt",
            success_url=reverse_lazy("core:new-password-link"),
        ),
        name="forget-password",
    ),
    # EXAMPLE PATH FOR KIRILL
    path("mobile/", TemplateView.as_view(template_name="about_example.html")),
    path("product/", TemplateView.as_view(template_name="about_example.html")),
    path("about/", TemplateView.as_view(template_name="about_example.html")),
    path("faq/", TemplateView.as_view(template_name="about_example.html")),
    path("pricing/", TemplateView.as_view(template_name="about_example.html")),
    path(
        "warranty/", TemplateView.as_view(template_name="about_example.html")
    ),
]

api_urlpatterns = [
    path(
        "create-subscription",
        login_required(CreateSubscriptionAPIView.as_view()),
        name="create-subscription",
    ),
    path("update-payment-method", UpdatePaymentMethodAPIView.as_view()),
    path("delete-payment-method", DeletePaymentMethodAPIView.as_view()),
    path(
        "cancel-subscription",
        CancelSubscriptionAPIView.as_view(),
        name="cancel-subscription",
    ),
    path("device-owner", DeviceOwnerApiView.as_view()),
]

urlpatterns = view_urlpatterns + api_urlpatterns
