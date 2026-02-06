from allauth.account.decorators import secure_admin_login
from allauth.socialaccount import admin as socialaccount_admin
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.models import SocialToken
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


# Unregister default admin classes to apply Unfold styling
admin.site.unregister(Group)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)


class SocialAppForm(forms.ModelForm):
    """Custom SocialApp form with Unfold styling for text fields."""

    class Meta:
        model = SocialApp
        fields = [
            "provider",
            "provider_id",
            "name",
            "client_id",
            "secret",
            "key",
            "settings",
        ]
        widgets = {
            "client_id": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "focus:border-blue-500"
                    ),
                    "placeholder": "Enter client ID",
                }
            ),
            "secret": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "focus:border-blue-500"
                    ),
                    "placeholder": "Enter secret key",
                }
            ),
            "key": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "focus:border-blue-500"
                    ),
                    "placeholder": "Enter key (if required)",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "focus:border-blue-500"
                    ),
                    "placeholder": "Enter application name",
                }
            ),
        }


@admin.register(Group)
class GroupAdmin(auth_admin.GroupAdmin, ModelAdmin):
    pass


@admin.register(SocialApp)
class SocialAppAdmin(socialaccount_admin.SocialAppAdmin, ModelAdmin):
    form = SocialAppForm


@admin.register(SocialAccount)
class SocialAccountAdmin(socialaccount_admin.SocialAccountAdmin, ModelAdmin):
    pass


@admin.register(SocialToken)
class SocialTokenAdmin(socialaccount_admin.SocialTokenAdmin, ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin, ModelAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (_("Subscription"), {"fields": ("has_membership", "membership_paused")}),
        (_("Stripe"), {"fields": ("stripe_customer_id", "stripe_dashboard_link")}),
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
    list_display = [
        "email",
        "name",
        "is_superuser",
        "stripe_customer",
        "has_membership",
        "membership_paused",
    ]
    search_fields = ["name"]
    readonly_fields = ("stripe_customer_id", "stripe_dashboard_link")

    def stripe_customer(self, obj):
        """Display stored Stripe customer ID."""
        return obj.stripe_customer_id or "-"

    stripe_customer.short_description = "Stripe Customer"

    def stripe_dashboard_link(self, obj):
        """Link to the Stripe dashboard for the stored customer."""
        if not obj.stripe_customer_id:
            return "-"
        base_url = "https://dashboard.stripe.com"
        if not settings.STRIPE_LIVE_MODE:
            base_url = f"{base_url}/test"
        url = f"{base_url}/customers/{obj.stripe_customer_id}"
        return format_html(
            '<a href="{url}" target="_blank" rel="noopener">{label}</a>',
            url=url,
            label="View in Stripe",
        )

    stripe_dashboard_link.short_description = "Stripe Dashboard"
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
