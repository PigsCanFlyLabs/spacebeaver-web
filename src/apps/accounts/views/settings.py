from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from templated_email import send_templated_mail

from apps.core.consts import ProfileStepsEnum


User = get_user_model()


class SettingsForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Type your email", "readonly": "readonly"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "***********", "readonly": "readonly"}
        ),
    )

    class Meta:
        model = User
        fields = ["email", "password"]


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )


class ChangePasswordForm(forms.Form):
    password_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )


class SettingsView(View):
    template_name = "accounts_form.html"
    form_class = SettingsForm

    def get(self, request):
        form = self.form_class(
            initial={
                "email": request.user.email,
                "password": "****************",
            }
        )

        change_email_form = ChangeEmailForm()
        change_password_form = ChangePasswordForm()
        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "form": form,
                "change_email_form": change_email_form,
                "change_password_form": change_password_form,
            },
        )

    def post(self, request):
        print(request.POST)

        form = None
        change_email = True
        if "email" in request.POST:
            form = ChangeEmailForm(request.POST)
        elif "password_email" in request.POST:
            form = ChangePasswordForm(request.POST)
            change_email = False

        if form:
            if form.is_valid():
                email_template = (
                    "change_email_confirmation"
                    if change_email
                    else "change_password_confirmation"
                )
                send_templated_mail(
                    email_template,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    {"username": request.user.full_name, "reset_url": ""},
                )

        return self.get(request)

    @property
    def base_context(self):
        return {
            "title": "Settings",
            "navname": "Settings",
            "action": reverse("accounts:profile"),
            "action_button_name": "Save",
            "step": ProfileStepsEnum.SETTINGS.value,
        }
