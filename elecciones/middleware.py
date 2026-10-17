from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import resolve


class RolePermissionMiddleware:
    """Protege el bloque administrativo con grupos y permisos de Django."""

    ADMINISTRATIVE_GROUPS = {
        "Administrador general",
        "Configurador",
        "Operador",
        "Publicador",
        "Auditor",
    }

    ROUTE_PERMISSIONS = {
        "elecciones:categorias_lista": "elecciones.view_categoria",
        "elecciones:categoria_crear": "elecciones.add_categoria",
        "elecciones:categoria_editar": "elecciones.change_categoria",
        "elecciones:categoria_estado": "elecciones.change_categoria",
        "elecciones:categorias_copiar": "elecciones.add_categoria",
        "elecciones:votaciones_lista": "elecciones.view_votacion",
        "elecciones:votacion_crear": "elecciones.add_votacion",
        "elecciones:votacion_editar": "elecciones.change_votacion",
        "elecciones:votacion_publicacion": "elecciones.publicar_votacion",
        "elecciones:votacion_estado": "elecciones.operar_votacion",
        "elecciones:resultados_lista": "elecciones.view_voto",
        "elecciones:resultado_detalle_admin": "elecciones.view_voto",
        "elecciones:publicar_resultado": "elecciones.add_publicacionresultado",
        "elecciones:retirar_resultado": "elecciones.change_publicacionresultado",
        "elecciones:auditoria_lista": "elecciones.view_eventoauditoria",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    @classmethod
    def _has_administrative_role(cls, user):
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=cls.ADMINISTRATIVE_GROUPS).exists()

    def __call__(self, request):
        if not request.path_info.startswith("/administracion/"):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not self._has_administrative_role(request.user):
            raise PermissionDenied(
                "La cuenta no tiene un rol administrativo asignado."
            )

        match = resolve(request.path_info)
        permission = self.ROUTE_PERMISSIONS.get(match.view_name)
        if (
            permission
            and not request.user.is_superuser
            and not request.user.has_perm(permission)
        ):
            raise PermissionDenied(
                "La cuenta no tiene permiso para esta operacion."
            )

        return self.get_response(request)
