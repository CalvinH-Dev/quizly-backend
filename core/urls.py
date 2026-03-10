from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"status": "ok", "message": "Server is running"})


urlpatterns = [
    path("", health_check, name="health_check"),
    path("api/", include("auth_app.api.urls")),
    path("api/", include("quiz_app.api.urls")),
    path("admin/", admin.site.urls),
]
