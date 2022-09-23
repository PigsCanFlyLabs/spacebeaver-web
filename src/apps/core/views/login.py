from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import render
from django.urls import reverse

from apps.core.consts import OnboardingStepsEnum
from apps.core.forms import LoginForm


User = get_user_model()


def login_routing(user: User):
    """
    Select page based on profile status
    """

    if user.last_wizard_step == OnboardingStepsEnum.DETAILS.value:
        return reverse("core:personal-info")
    elif user.last_wizard_step == OnboardingStepsEnum.ADD_DEVICE.value:
        return reverse("core:add-device")
    elif user.last_wizard_step == OnboardingStepsEnum.PICK_PLAN.value:
        return reverse("core:pick-plan")
    elif user.last_wizard_step == OnboardingStepsEnum.PAYMENT.value:
        return reverse("core:subscription")
    else:
        return reverse("core:dashboard")


class LoginView(BaseLoginView):
    template_name = "login.html"

    def get_success_url(self):
        return login_routing(self.request.user)
