from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from .models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def send_mail(self, template_prefix, email, context):
        """
        Send HTML-only emails for account notifications.
        """
        subject_file = f"{template_prefix}_subject.txt"
        html_file = f"{template_prefix}_message.html"

        # Add extra context
        context["site_url"] = getattr(settings, "BASE_URL", "https://competibee.com")
        context["user_email"] = email

        # Get the subject
        subject = render_to_string(subject_file, context).strip()
        subject = " ".join(subject.split())  # Remove extra whitespace

        # Get HTML content
        try:
            html_content = render_to_string(html_file, context)
        except (FileNotFoundError, ValueError, TypeError):
            # Fallback to default allauth behavior if HTML template fails
            super().send_mail(template_prefix, email, context)
            return

        # Create HTML-only email
        from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", "temp competibee <noreply@competibee.com>"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=(
                "This email requires HTML support. "
                "Please enable HTML emails in your email client."
            ),
            from_email=from_email,
            to=[email],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
