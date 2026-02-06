"""
With these settings, tests run faster.
"""

from .base import *  # noqa: F403
from .base import MIDDLEWARE
from .base import TEMPLATES
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# Disable DEBUG to prevent debug_toolbar middleware from loading
DEBUG = False

# Remove debug_toolbar and browser_reload middleware for tests
# (they're added conditionally in base.py based on DEBUG at import time)
MIDDLEWARE = [
    m for m in MIDDLEWARE if "debug_toolbar" not in m and "browser_reload" not in m
]

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="!!!SET DJANGO_SECRET_KEY!!!",
)
TEST_RUNNER = "django.test.runner.DiscoverRunner"

STRIPE_SECRET_KEY = "sk_test_1234567890"  # noqa: S105
STRIPE_WEBHOOK_SECRET = "whsec_test_1234567890"  # noqa: S105

# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore[index]

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_URL = "http://media.testserver/"

# FRONTEND URL
# ------------------------------------------------------------------------------
FRONTEND_URL = "http://testserver"
