import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
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
    new_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your new email"}),
    )


class SendResetPasswordForm(forms.Form):
    password_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="New password", widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label="Confirm new password", widget=forms.PasswordInput()
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
        reset_password_form = SendResetPasswordForm()
        change_password_form = ResetPasswordForm()

        change_email = request.GET.get("change_email", None)
        reset_password = "reset_password" in request.GET

        if reset_password:
            if timezone.now() > (
                request.user.email_reset_request_time
                + datetime.timedelta(days=3)
            ):
                self.expired_link = True

        if change_email:
            if timezone.now() < (
                request.user.email_reset_request_time
                + datetime.timedelta(days=3)
            ):
                request.user.customer.email = change_email
                request.user.customer.save()
                request.user.email = change_email
                request.user.save()
                self.email_changed_notification = True

            else:
                self.expired_link = True

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "form": form,
                "reset_password_form": reset_password_form,
                "change_email_form": change_email_form,
                "change_password_form": change_password_form,
                "show_email_notification": getattr(
                    self, "show_email_notification", False
                ),
                "show_password_notification": getattr(
                    self, "show_password_notification", False
                ),
                "password_changed_notification": getattr(
                    self, "password_changed_notification", False
                ),
                "email_changed_notification": getattr(
                    self, "email_changed_notification", False
                ),
                "expired_link": getattr(self, "expired_link", False),
            },
        )

    def post(self, request):

        change_email = True
        self.show_email_notification = False
        self.password_changed_notification = False
        self.email_changed_notification = False
        self.successfuly_changed = False
        self.expired_link = False

        if "password_email" in request.POST:
            form = SendResetPasswordForm(request.POST)
            change_email = False
            if form.is_valid():
                request.user.password_reset_request_time = timezone.now()
                self.send_confirmation_email(request, change_email)
                self.show_password_notification = True

        elif "new_email" in request.POST:
            form = ChangeEmailForm(request.POST)
            if form.is_valid():
                request.user.email_reset_request_time = timezone.now()
                request.user.save()
                self.change_email_url(request, form.cleaned_data["new_email"])
                self.show_email_notification = True

        elif "password1" in request.POST and "password2" in request.POST:
            form = ResetPasswordForm(request.POST)
            if form.is_valid():

                if timezone.now() < (
                    request.user.password_reset_request_time
                    + datetime.timedelta(days=3)
                ):
                    new_password1 = form.cleaned_data["password1"]
                    new_password2 = form.cleaned_data["password2"]

                    if new_password1 == new_password2:
                        request.user.set_password(new_password1)
                        request.user.save()
                    user = authenticate(
                        username=request.user.email,
                        password=form.cleaned_data["password1"],
                    )
                    login(request, user)
                    self.password_changed_notification = True
                else:
                    self.expired_link = True

        return self.get(request)

    def change_email_url(self, request, new_email):
        reset_url = f"{request.build_absolute_uri()}?change_email={new_email}"
        email_template = "change_email_confirmation"
        send_templated_mail(
            email_template,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            {"username": request.user.full_name, "reset_url": reset_url},
        )

    def send_confirmation_email(self, request, change_email):
        reset_url = f"{request.build_absolute_uri()}?" + (
            "reset_email" if change_email else "reset_password"
        )

        email_template = (
            "change_email_confirmation"
            if change_email
            else "change_password_confirmation"
        )
        send_templated_mail(
            email_template,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            {"username": request.user.full_name, "reset_url": reset_url},
        )

    @property
    def base_context(self):
        return {
            "title": "Settings",
            "navname": "Settings",
            "action": reverse("accounts:profile"),
            "action_button_name": "Save",
            "step": ProfileStepsEnum.SETTINGS.value,
        }
