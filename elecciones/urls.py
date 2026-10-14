from django.urls import path
from . import views

app_name = "elecciones"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("votaciones/<slug:slug>/", views.detalle, name="detalle"),
    path("administracion/", views.panel, name="panel"),
]
