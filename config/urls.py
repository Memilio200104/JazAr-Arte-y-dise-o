from django.http import JsonResponse
from django.urls import include, path


def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", include("website.urls")),
    path("healthz/", healthz, name="healthz"),
]
