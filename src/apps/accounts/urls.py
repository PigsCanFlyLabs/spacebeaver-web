# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.accounts.views import (
    ChangeEmailView,
    PasswordChangeView,
    ProfileView,
    SettingsView,
)
from apps.core.views import LoginView


app_name = "accounts"

urlpatterns = [
    path("profile", login_required(ProfileView.as_view()), name="profile"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "settings",
        SettingsView.as_view(),
        name="settings",
    ),
    path("logout", LogoutView.as_view(next_page="/"), name="logout"),
    path("change-email", ChangeEmailView.as_view(), name="change-email"),
    path(
        "change-password", PasswordChangeView.as_view(), name="change-password"
    ),
]
