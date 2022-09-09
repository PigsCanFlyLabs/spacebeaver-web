import datetime
import uuid

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from templated_email import send_templated_mail

from apps.accounts.models.user import EmailChangeAuth
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


class ResetPasswordFormWithToken(ResetPasswordForm):
    change_token = forms.CharField()


class SettingsView(View):
    template_name = "accounts_form.html"
    form_class = SettingsForm

    def get(self, request):

        if not request.user.is_authenticated:
            if "change_email" in request.GET:
                reversed_url = reverse("accounts:change-email")
                return redirect(
                    f"{reversed_url}?change_email={request.GET.get('change_email')}"
                )
            elif "change_password" in request.GET:
                reversed_url = reverse("accounts:change-password")
                return redirect(
                    f"{reversed_url}?change_password={request.GET.get('change_password')}"
                )
            else:
                return redirect(reverse("accounts:login"))

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
        reset_password = "change_password" in request.GET

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
                email_change = EmailChangeAuth.objects.filter(
                    uuid=change_email
                ).first()
                if email_change:
                    customer = request.user.customer
                    if customer:
                        request.user.customer.email = email_change.new_email
                        request.user.customer.save()
                    request.user.email = email_change.new_email
                    request.user.save()
                    self.email_changed_notification = True
                    email_change.delete()
                else:
                    self.expired_link = True
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
                "show_exists_email_notification": getattr(
                    self, "show_exists_email_notification", False
                ),
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
                self.send_change_password_letter(request, change_email)
                self.show_password_notification = True

        elif "new_email" in request.POST:
            form = ChangeEmailForm(request.POST)
            if form.is_valid():
                new_emal = form.cleaned_data["new_email"]
                email_exists = User.objects.filter(email=new_emal).first()
                if email_exists and email_exists != request.user:
                    self.show_exists_email_notification = True
                else:
                    request.user.email_reset_request_time = timezone.now()
                    request.user.save()
                    self.send_change_email_letter(request, new_emal)
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
                    EmailChangeAuth.objects.filter(
                        user_id=request.user.id, new_email="password1234"
                    ).delete()
                    self.password_changed_notification = True
                else:
                    self.expired_link = True

        return self.get(request)

    def send_change_email_letter(self, request, new_email):

        change_mail_uuid = uuid.uuid4()
        EmailChangeAuth.objects.create(
            new_email=new_email, uuid=change_mail_uuid, user=request.user
        )

        reset_url = (
            f"{request.build_absolute_uri()}?change_email={change_mail_uuid}"
        )
        email_template = "change_email_confirmation.email"
        send_templated_mail(
            email_template,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            {
                "username": request.user.full_name,
                "reset_url": reset_url,
                "root_link": request._current_scheme_host,
            },
        )

    def send_change_password_letter(self, request, change_email):
        change_password_uuid = uuid.uuid4()
        EmailChangeAuth.objects.create(
            new_email="password1234",
            uuid=change_password_uuid,
            user=request.user,
        )

        reset_url = f"{request.build_absolute_uri()}?change_password={change_password_uuid}"
        send_templated_mail(
            "change_password_confirmation",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            {
                "username": request.user.full_name,
                "reset_url": reset_url,
                "root_link": request._current_scheme_host,
            },
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


class ChangeEmailView(View):
    template_name = "email_change_page.html"

    def get(self, request):
        context = {}
        if "change_email" in request.GET:
            change_email_token = request.GET.get("change_email")
            email_change = EmailChangeAuth.objects.filter(
                uuid=change_email_token
            ).first()
            if email_change:
                if timezone.now() < (
                    email_change.user.email_reset_request_time
                    + datetime.timedelta(days=3)
                ):
                    customer = email_change.user.customer
                    if customer:
                        customer.email = email_change.new_email
                        customer.save()
                    email_change.user.email = email_change.new_email
                    email_change.user.save()
                    email_change.delete()
                    context.update({"new_email": email_change.new_email})
            else:
                context.update({"expired_link": True})
        else:
            context.update({"expired_link": True})

        return render(request, self.template_name, context)


class PasswordChangeView(View):
    template_name = "password_change_page.html"

    def get(self, request):
        context = {}
        form = ResetPasswordForm()
        change_token = request.GET.get("change_password", None)
        if change_token:
            change_link = EmailChangeAuth.objects.filter(
                uuid=change_token
            ).filter()
            if change_link:
                context.update({"change_token": change_token})
            else:
                context.update({"expired_link": True})
        else:
            context.update({"expired_link": True})

        return render(request, self.template_name, {"form": form, **context})

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            change_email_token = request.POST.get("change_token")
            change_entity = EmailChangeAuth.objects.filter(
                uuid=change_email_token
            ).first()
            if change_entity:
                if timezone.now() < (
                    change_entity.user.password_reset_request_time
                    + datetime.timedelta(days=3)
                ):
                    new_password1 = form.cleaned_data["password1"]
                    new_password2 = form.cleaned_data["password2"]

                    if new_password1 == new_password2:
                        change_entity.user.set_password(new_password1)
                        change_entity.user.save()
                    EmailChangeAuth.objects.filter(
                        uuid=change_email_token
                    ).delete()
                    self.password_changed_notification = True
            else:
                self.expired_link = True

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "password_changed_notification": getattr(
                    self, "password_changed_notification", False
                ),
            },
        )
