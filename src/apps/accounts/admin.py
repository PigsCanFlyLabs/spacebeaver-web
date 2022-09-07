# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import User
from apps.accounts.models.user import EmailChangeAuth


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "full_name",
                    "external_email",
                    "external_phone",
                    "last_wizard_step",
                    "selected_plan",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(EmailChangeAuth)
class EmailChangeAuthAdmin(admin.ModelAdmin):
    list_display = ("new_email", "user")
