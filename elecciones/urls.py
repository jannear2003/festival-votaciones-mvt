from django.urls import path
from . import views
app_name="elecciones"
urlpatterns=[path("",views.inicio,name="inicio"),path("votaciones/<slug:slug>/",views.detalle,name="detalle"),path("administracion/",views.panel,name="panel"),path("administracion/categorias/",views.categorias_lista,name="categorias_lista"),path("administracion/categorias/nueva/",views.categoria_crear,name="categoria_crear"),path("administracion/categorias/<int:pk>/editar/",views.categoria_editar,name="categoria_editar"),path("administracion/categorias/<int:pk>/<str:accion>/",views.categoria_estado,name="categoria_estado"),path("administracion/categorias/copiar/",views.categorias_copiar,name="categorias_copiar")]
