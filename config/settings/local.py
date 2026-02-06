import os
import socket

from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import TEMPLATES
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="SmyuNFv2uu0PWiH2IZCwgpJDWtahoWrbtpD1Dev8FgxgVvBB4KjOuWTsp6zpat6u",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

# CACHES
# ------------------------------------------------------------------------------
# Using dummy cache for development to avoid cache-related issues during development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

# EMAIL
# ------------------------------------------------------------------------------

EMAIL_HOST = env("EMAIL_HOST", default="mailpit")
EMAIL_PORT = 1025


hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [".".join([*ip.split(".")[:-1], "1"]) for ip in ips]

BASE_URL = "http://localhost:8000"

INSTALLED_APPS += ["django_extensions", "debug_toolbar", "django_browser_reload"]
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
TEMPLATES[0]["APP_DIRS"] = False
# Force Django to use StatReloader with polling
os.environ.setdefault("DJANGO_WATCHMAN_TIMEOUT", "2")
os.environ.setdefault("DJANGO_AUTORELOAD_USE_WATCHMAN", "0")

# Ensure browser reload works with Docker polling
DJANGO_BROWSER_RELOAD_ENABLE = True
DJANGO_BROWSER_RELOAD_DELAY = 500  # milliseconds
FRONTEND_URL = "http://localhost:4000"
