from django.http import JsonResponse
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

handler400 = 'website.errors.bad_request'
handler403 = 'website.errors.permission_denied'
handler404 = 'website.errors.page_not_found'
handler500 = 'website.errors.server_error'


def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('', include('payments.urls')),
    path('admin/', admin.site.urls),
    path("", include("website.urls")),
    path("healthz/", healthz, name="healthz"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
