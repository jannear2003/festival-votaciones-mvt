from django.contrib import admin
from django.urls import include, path
from elecciones.views import LoginPorRolView

urlpatterns = [
    path(
        "cuentas/login/",
        LoginPorRolView.as_view(),
        name="login",
    ),
    path("admin/", admin.site.urls),
    path("cuentas/", include("django.contrib.auth.urls")),
    path("", include("elecciones.urls")),
]
