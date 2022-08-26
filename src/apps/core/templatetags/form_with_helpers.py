from django import template


register = template.Library()


@register.inclusion_tag("templatetags/form_with_helpers.html")
def form_with_helpers(
    form,
    action,
    action_button_name="Create account",
    change_email_form=None,
    change_password_form=None,
):
    return {
        "form": form,
        "action": action,
        "button_name": action_button_name,
        "change_email_form": change_email_form,
        "change_password_form": change_password_form,
    }
