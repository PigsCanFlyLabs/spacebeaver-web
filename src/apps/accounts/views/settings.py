from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
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


class SendResetEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )


class SendResetPasswordForm(forms.Form):
    password_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )


class ResetEmailForm(forms.Form):
    new_email = forms.EmailField(
        label="New email",
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
        self.show_email_notification = False
        self.password_changed_notification = False
        self.successfuly_changed = False
        form = self.form_class(
            initial={
                "email": request.user.email,
                "password": "****************",
            }
        )
        reset_email_form = SendResetEmailForm()
        reset_password_form = SendResetPasswordForm()
        change_email_form = ResetEmailForm()
        change_password_form = ResetPasswordForm()
        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "form": form,
                "reset_email_form": reset_email_form,
                "reset_password_form": reset_password_form,
                "change_email_form": change_email_form,
                "change_password_form": change_password_form,
                "show_email_notification": getattr(
                    self, "show_email_notification", False
                ),
                "password_changed_notification": getattr(
                    self, "password_changed_notification", False
                ),
                "email_changed_notification": getattr(
                    self, "email_changed_notification", False
                ),
            },
        )

    def post(self, request):

        change_email = True
        self.show_email_notification = False
        self.password_changed_notification = False
        self.email_changed_notification = False
        self.successfuly_changed = False

        if "email" in request.POST:
            form = SendResetEmailForm(request.POST)
            if form.is_valid():
                self.send_confirmation_email(request, change_email)
        elif "password_email" in request.POST:
            form = SendResetPasswordForm(request.POST)
            change_email = False
            if form.is_valid():
                self.send_confirmation_email(request, change_email)
        elif "new_email" in request.POST:
            form = ResetEmailForm(request.POST)
            if form.is_valid():
                request.user.customer.email = form.cleaned_data["new_email"]
                request.user.customer.save()
                request.user.email = form.cleaned_data["new_email"]
                request.user.save()
                self.email_changed_notification = True

        elif "password1" in request.POST and "password2" in request.POST:
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
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

        return self.get(request)

    def send_confirmation_email(self, request, change_email):
        reset_url = f"{request.build_absolute_uri()}?" + (
            "reset_email" if change_email else "reset_password"
        )
        self.show_email_notification = True
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
