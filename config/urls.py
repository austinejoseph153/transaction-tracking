from django.contrib import admin
from django.urls import path, include
from django.views import defaults as default_views
from django.conf import settings
from django.contrib.auth.models import User
from django.conf.urls.static import static


urlpatterns = [
    path("", include('apps.pages.urls', namespace="pages")),
    path("", include('apps.user.urls', namespace="user")),
    path("", include('apps.transaction.urls', namespace="transaction")),
]

urlpatterns += [
    path(settings.ADMIN_URL, admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
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
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
