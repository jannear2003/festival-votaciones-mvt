from django import template

from elecciones.middleware import RolePermissionMiddleware

register = template.Library()


@register.filter
def has_admin_access(user):
    """Muestra enlaces administrativos solo a cuentas admitidas por middleware."""
    return RolePermissionMiddleware._has_administrative_role(user)
