from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from apps.api.api import api

urlpatterns = [
    path("api/", api.urls),
    # Allauth headless API endpoints
    path("_allauth/", include("allauth.headless.urls")),
    path("api/health/", lambda request: HttpResponse("OK"), name="health_check"),
    path(
        "api/csrf/",
        never_cache(
            require_http_methods(["GET"])(
                ensure_csrf_cookie(
                    lambda request: JsonResponse(
                        {"csrfToken": get_token(request), "status": "ok"}
                    )
                )
            )
        ),
        name="csrf_token",
    ),
    path("payments/", include("apps.payments.urls", namespace="payments")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("accounts/", include("allauth.urls")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
