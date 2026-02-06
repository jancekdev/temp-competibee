from allauth.account.models import EmailAddress
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def account_settings(request):
    """Account settings page with membership status and profile management."""
    user = request.user

    # Get user's primary email for verification status
    primary_email = EmailAddress.objects.filter(user=user, primary=True).first()

    context = {
        "user": user,
        "primary_email": primary_email,
    }

    return render(request, "users/account_settings.html", context)
