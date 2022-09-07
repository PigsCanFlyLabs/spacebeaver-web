from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from constance import config

from apps.core.consts import OnboardingStepsEnum
from apps.utils.stripe import create_subscription, delete_subscription


class PickPlanView(View):
    template = "pick_plan.html"

    def get(self, request):
        # customer_id = request.user.customer_id
        # subscription = Subscription.objects.filter(customer_id=customer_id).first()
        # context = self.base_context
        # if subscription:
        #     context.update({"selected_plan": subscription})

        return render(request, self.template, self.base_context)

    def post(self, request):
        request.user.selected_plan = 1
        if request.user.last_wizard_step <= 3:
            request.user.last_wizard_step += 1
        request.user.save()

        return redirect(reverse("core:subscription"))

    @property
    def base_context(self):
        return {
            "title": "Pick a plan",
            "navname": "Please, pick a plan",
            "plan_title": config.TITLE,
            "image": f"{settings.MEDIA_URL}{config.IMAGE}",
            "description": config.DESCRIPTION,
            "price": config.PRICE,
            "step": OnboardingStepsEnum.PICK_PLAN.value,
            "back_url": reverse("core:add-device"),
        }


class UpdatePlanForm(forms.Form):
    selected_plan = forms.IntegerField()


class UpdatePlanView(PickPlanView):
    template = "update_plan.html"

    def get(self, request):
        return render(request, self.template, self.base_context)

    def post(self, request):

        form = UpdatePlanForm(request.POST)
        if form.is_valid():
            customer = request.user.customer
            subscription = customer.subscriptions.filter(
                plan__id=config.STRIPE_PRICE_ID, status="active"
            ).first()
            if form.cleaned_data["selected_plan"] == -1:
                if subscription:
                    delete_subscription(subscription.id)
                request.user.selected_plan = 0
                request.user.save()
            else:
                if subscription:
                    delete_subscription(subscription.id)
                subscription = create_subscription(
                    config.STRIPE_PRICE_ID, customer.id
                )
                request.user.selected_plan = form.cleaned_data["selected_plan"]
                request.user.save()
        return self.get(request)
