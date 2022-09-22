from django.shortcuts import redirect

from apps.core.consts import OnboardingStepsEnum


BLOCKED_PAGES = (
    "/dashboard",
    "/billing",
    "/accounts/profile",
    "/accounts/settings",
    "/replace-device",
    "/blocked-numbers/",
)


def check_wizard_completed(get_response):
    def middleware(request):
        response = get_response(request)
        if (
            hasattr(request.user, "last_wizard_step")
            and request.user.last_wizard_step < 5
        ):
            for item in BLOCKED_PAGES:
                if item in request.path:
                    if (
                        request.user.last_wizard_step
                        == OnboardingStepsEnum.DETAILS.value
                    ):
                        return redirect("core:personal-info")
                    elif (
                        request.user.last_wizard_step
                        == OnboardingStepsEnum.ADD_DEVICE.value
                    ):
                        return redirect("core:add-device")
                    elif (
                        request.user.last_wizard_step
                        == OnboardingStepsEnum.PICK_PLAN.value
                    ):
                        return redirect("core:pick-plan")
                    elif (
                        request.user.last_wizard_step
                        == OnboardingStepsEnum.PAYMENT.value
                    ):
                        return redirect("core:subscription")

                    return redirect("core:personal-info")
        return response

    return middleware
