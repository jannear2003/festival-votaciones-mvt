from pathlib import Path

from django.core.exceptions import ValidationError


EXTENSIONES_IMAGEN_PERMITIDAS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

TIPOS_IMAGEN_PERMITIDOS = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

TAMANO_MAXIMO_IMAGEN = 5 * 1024 * 1024


def validar_imagen_configurable(archivo):
    if not archivo:
        return

    extension = Path(archivo.name).suffix.lower()

    if extension not in EXTENSIONES_IMAGEN_PERMITIDAS:
        raise ValidationError(
            "Formato no permitido. Utilice JPEG, PNG o WebP."
        )

    if archivo.size > TAMANO_MAXIMO_IMAGEN:
        raise ValidationError(
            "La imagen no puede superar 5 MB."
        )

    content_type = getattr(
        archivo,
        "content_type",
        None,
    )

    if (
        content_type
        and content_type not in TIPOS_IMAGEN_PERMITIDOS
    ):
        raise ValidationError(
            "El tipo de archivo no corresponde a una imagen "
            "JPEG, PNG o WebP."
        )
