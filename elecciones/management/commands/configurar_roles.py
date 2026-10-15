from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from elecciones.models import Votacion


ROLE_PERMISSIONS = {
    'Administrador general': ['*'],
    'Configurador': [
        'view_festival', 'view_edicion',
        'view_categoria', 'add_categoria', 'change_categoria',
        'view_tipovotacion',
        'view_votacion', 'add_votacion', 'change_votacion', 'publicar_votacion',
        'view_opcion', 'add_opcion', 'change_opcion', 'delete_opcion',
    ],
    'Operador': [
        'view_edicion', 'view_categoria',
        'view_votacion', 'operar_votacion',
        'view_opcion',
        'view_participacion', 'view_voto',
    ],
    'Publicador': [
        'view_edicion', 'view_categoria', 'view_votacion',
        'view_opcion', 'view_participacion', 'view_voto',
        'view_publicacionresultado', 'add_publicacionresultado',
        'change_publicacionresultado',
    ],
    'Auditor': [
        'view_festival', 'view_edicion', 'view_categoria',
        'view_tipovotacion', 'view_votacion', 'view_opcion',
        'view_participacion', 'view_voto',
        'view_publicacionresultado', 'view_eventoauditoria',
    ],
}


class Command(BaseCommand):
    help = 'Crea o actualiza roles y separa permisos estructurales, operativos y de publicación.'

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Votacion)
        Permission.objects.get_or_create(
            content_type=content_type,
            codename='operar_votacion',
            defaults={'name': 'Puede abrir y cerrar votaciones'},
        )
        Permission.objects.get_or_create(
            content_type=content_type,
            codename='publicar_votacion',
            defaults={'name': 'Puede publicar y retirar votaciones del portal'},
        )

        app_permissions = Permission.objects.filter(content_type__app_label='elecciones')
        available = {permission.codename: permission for permission in app_permissions}

        for role_name, codenames in ROLE_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            if codenames == ['*']:
                selected = list(app_permissions)
            else:
                selected = [available[codename] for codename in codenames if codename in available]
                missing = [codename for codename in codenames if codename not in available]
                if missing:
                    self.stdout.write(self.style.WARNING(
                        f'{role_name}: permisos no encontrados: {", ".join(missing)}'
                    ))
            group.permissions.set(selected)
            self.stdout.write(self.style.SUCCESS(
                f'{role_name}: {len(selected)} permisos configurados.'
            ))

        self.stdout.write(self.style.SUCCESS('Roles y permisos separados correctamente.'))
