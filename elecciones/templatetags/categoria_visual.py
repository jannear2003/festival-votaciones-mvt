from django import template

register = template.Library()

@register.filter
def categoria_imagen(categoria):
    if categoria is None:
        return "images/categories/categoria-general.webp"

    nombre = str(getattr(categoria, "nombre", "") or "").casefold()
    descripcion = str(getattr(categoria, "descripcion", "") or "").casefold()
    texto = f"{nombre} {descripcion}"

    palabras_cancion = (
        "cancion", "canción", "inedita", "inédita",
        "composicion", "composición", "compositor", "autor",
    )
    palabras_juvenil = (
        "juvenil", "joven", "infantil", "menor", "niñez",
    )
    palabras_acordeon = (
        "acordeon", "acordeón", "rey vallenato", "profesional",
        "aficionado", "acordeonera",
    )

    if any(palabra in texto for palabra in palabras_cancion):
        return "images/categories/categoria-cancion.webp"
    if any(palabra in texto for palabra in palabras_juvenil):
        return "images/categories/categoria-juvenil.webp"
    if any(palabra in texto for palabra in palabras_acordeon):
        return "images/categories/categoria-acordeon.webp"
    return "images/categories/categoria-general.webp"


from django.templatetags.static import static


@register.simple_tag
def votacion_imagen_url(votacion):
    """
    Devuelve la imagen principal de una votación siguiendo esta prioridad:

    1. Imagen configurada en la votación.
    2. Imagen configurada en la categoría.
    3. Recurso estático seleccionado por categoria_imagen.
    """
    if votacion is None:
        return static(
            "images/categories/categoria-general.webp"
        )

    imagen_votacion = getattr(
        votacion,
        "imagen",
        None,
    )

    if imagen_votacion:
        try:
            return imagen_votacion.url
        except (ValueError, OSError):
            pass

    categoria = getattr(
        votacion,
        "categoria",
        None,
    )

    imagen_categoria = getattr(
        categoria,
        "imagen",
        None,
    )

    if imagen_categoria:
        try:
            return imagen_categoria.url
        except (ValueError, OSError):
            pass

    return static(
        categoria_imagen(categoria)
    )


@register.simple_tag
def votacion_respaldo_url(votacion):
    """
    Devuelve siempre un recurso estático para utilizarlo si falla
    una imagen cargada en media.
    """
    categoria = getattr(
        votacion,
        "categoria",
        None,
    )

    return static(
        categoria_imagen(categoria)
    )
