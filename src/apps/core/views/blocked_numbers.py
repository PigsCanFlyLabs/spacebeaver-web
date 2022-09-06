from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from apps.core.consts import ProfileStepsEnum
from apps.core.forms import BlockedNumberForm
from apps.core.models import BlockedNumber


class BlockedNumbersView(View):
    template = "blocked_numbers.html"
    form_class = BlockedNumberForm
    page_size = 10

    def get(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        numbers = BlockedNumber.object.get_user_blocked_numbers(
            request.user
        ).values("id", "number", "name")
        paginator = Paginator(numbers, self.page_size)
        page = paginator.get_page(request.GET.get("page", 1))
        form = self.form_class()
        return render(
            request,
            self.template,
            {**self.base_context, "page": page, "form": form, **extra_context},
        )

    def post(self, request):
        form = self.form_class(request.POST)
        self.success_notification = False
        if form.is_valid():
            self.success_notification = True
            BlockedNumber.object.add_user_blocked_number(
                form.cleaned_data["name"],
                form.cleaned_data["number"],
                request.user,
            )
            self.blocked_number = form.cleaned_data["number"]
            return self.get(request)
        return self.get(request, {"form": form, "error": True})

    @property
    def base_context(self):
        return {
            "title": "Blocked numbers",
            "navname": "Blocked numbers",
            "step": ProfileStepsEnum.SETTINGS.value,
            "show_success_notification": getattr(
                self, "success_notification", False
            ),
            "show_success_unblock_notification": getattr(
                self, "show_success_unblock_notification", False
            ),
            "blocked_number": getattr(self, "blocked_number", ""),
            "unblocked_number": getattr(self, "unblocked_number", ""),
        }


class DeleteBlockedNumberView(BlockedNumbersView):
    def post(self, request, pk):
        unblocked_number = BlockedNumber.object.delete_user_blocked_number(
            pk, request.user
        )
        self.show_success_unblock_notification = True
        self.unblocked_number = unblocked_number.number
        return self.get(request)


__all__ = ["DeleteBlockedNumberView", "BlockedNumbersView"]
