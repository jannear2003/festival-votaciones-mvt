import django.db.models.deletion
from django.db import migrations, models


def completar_categoria_y_edicion(apps, schema_editor):
    Participacion = apps.get_model(
        "elecciones",
        "Participacion",
    )

    participaciones = Participacion.objects.select_related(
        "votacion__categoria__edicion"
    ).all()

    for participacion in participaciones.iterator():
        categoria = participacion.votacion.categoria

        participacion.categoria_id = categoria.pk
        participacion.edicion_id = categoria.edicion_id
        participacion.save(
            update_fields=[
                "categoria",
                "edicion",
            ]
        )


def validar_datos_completos(apps, schema_editor):
    Participacion = apps.get_model(
        "elecciones",
        "Participacion",
    )

    incompletas = Participacion.objects.filter(
        models.Q(categoria__isnull=True)
        | models.Q(edicion__isnull=True)
    )

    if incompletas.exists():
        raise RuntimeError(
            "Existen participaciones sin categoría o edición."
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "elecciones",
            "0005_imagenes_configurables",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="participacion",
            name="categoria",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participaciones",
                to="elecciones.categoria",
            ),
        ),
        migrations.AddField(
            model_name="participacion",
            name="edicion",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participaciones",
                to="elecciones.edicion",
            ),
        ),
        migrations.RunPython(
            completar_categoria_y_edicion,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            validar_datos_completos,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="participacion",
            name="categoria",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participaciones",
                to="elecciones.categoria",
            ),
        ),
        migrations.AlterField(
            model_name="participacion",
            name="edicion",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participaciones",
                to="elecciones.edicion",
            ),
        ),
        migrations.AddConstraint(
            model_name="participacion",
            constraint=models.UniqueConstraint(
                fields=(
                    "usuario",
                    "edicion",
                    "categoria",
                ),
                name=(
                    "una_participacion_por_"
                    "usuario_edicion_categoria"
                ),
            ),
        ),
    ]
