from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, reverse


class RolePermissionMiddleware:
    """Autoriza rutas administrativas según permisos de Django.

    Los superusuarios conservan acceso total. Los usuarios autenticados sin el
    permiso requerido reciben un mensaje y regresan al panel administrativo.
    """

    ROUTE_PERMISSIONS = {
        # Categorías
        'elecciones:categorias_lista': 'elecciones.view_categoria',
        'elecciones:categoria_nueva': 'elecciones.add_categoria',
        'elecciones:categoria_editar': 'elecciones.change_categoria',
        'elecciones:categoria_estado': 'elecciones.change_categoria',
        'elecciones:categorias_copiar': 'elecciones.add_categoria',
        # Votaciones y opciones
        'elecciones:votaciones_lista': 'elecciones.view_votacion',
        'elecciones:votacion_nueva': 'elecciones.add_votacion',
        'elecciones:votacion_editar': 'elecciones.change_votacion',
        'elecciones:votacion_publicacion': 'elecciones.change_votacion',
        'elecciones:votacion_cerrar': 'elecciones.change_votacion',
        # Resultados
        'elecciones:resultados_lista': 'elecciones.view_voto',
        'elecciones:resultado_detalle_admin': 'elecciones.view_voto',
        'elecciones:publicar_resultado': 'elecciones.add_publicacionresultado',
        'elecciones:retirar_resultado': 'elecciones.change_publicacionresultado',
        # Auditoría
        'elecciones:auditoria_lista': 'elecciones.view_eventoauditoria',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        match = resolve(request.path_info)
        permission = self.ROUTE_PERMISSIONS.get(match.view_name)
        if permission:
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.get_full_path()}")
            if not request.user.is_superuser and not request.user.has_perm(permission):
                messages.error(request, 'No cuenta con permisos para realizar esta operación.')
                return redirect('elecciones:panel')
        return self.get_response(request)
