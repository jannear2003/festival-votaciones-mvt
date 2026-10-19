from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Participante(models.Model):
    class Tipo(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Individual"
        AGRUPACION = "AGRUPACION", "Agrupación"

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="participantes_responsables",
        verbose_name="cuenta responsable",
    )
    tipo = models.CharField(
        "tipo de participante",
        max_length=15,
        choices=Tipo.choices,
    )
    nombre_artistico = models.CharField(
        "nombre artístico",
        max_length=150,
    )
    nombre_legal = models.CharField(
        "nombre legal",
        max_length=200,
        blank=True,
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
    )
    pais = models.CharField(
        "país",
        max_length=100,
        default="Colombia",
    )
    correo_contacto = models.EmailField(
        "correo de contacto",
        blank=True,
    )
    telefono_contacto = models.CharField(
        "teléfono de contacto",
        max_length=30,
        blank=True,
    )
    biografia = models.TextField(
        "reseña artística",
        blank=True,
    )
    fotografia = models.ImageField(
        "fotografía o imagen",
        upload_to="participantes/",
        blank=True,
    )
    activo = models.BooleanField(
        default=True,
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "participante"
        verbose_name_plural = "participantes"
        ordering = ["nombre_artistico"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "responsable",
                    "tipo",
                    "nombre_artistico",
                ],
                name="participante_unico_por_responsable_tipo_nombre",
            )
        ]

    def clean(self):
        errors = {}

        if not self.nombre_artistico.strip():
            errors["nombre_artistico"] = (
                "El nombre artístico es obligatorio."
            )

        if (
            self.tipo == self.Tipo.INDIVIDUAL
            and not self.nombre_legal.strip()
        ):
            errors["nombre_legal"] = (
                "El nombre legal es obligatorio para un participante "
                "individual."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.nombre_artistico
