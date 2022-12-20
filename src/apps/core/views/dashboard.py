from django.shortcuts import render
from django.views import View

from apps.core.consts import ProfileStepsEnum
from apps.core.models import Device
from apps.core.services import get_user_message_count


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        user = request.user
        # TODO select all in single query

        device = Device.objects.filter(user_id=request.user.id).first()

        daily_message_count = get_user_message_count(
            user.twillion_number, "day"
        )
        monthly_message_count = get_user_message_count(
            user.twillion_number, "month"
        )
        yearly_message_count = get_user_message_count(
            user.twillion_number, "year"
        )
        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "daily": daily_message_count,
                "monthly": monthly_message_count,
                "yearly": yearly_message_count,
                "external_phone": device.external_phone if device else None,
                "external_email": device.external_email if device else None,
            },
        )

    @property
    def base_context(self):
        return {
            "title": "Dashboard",
            "navname": "Dashboard",
            "step": ProfileStepsEnum.DASHBOARD.value,
        }
