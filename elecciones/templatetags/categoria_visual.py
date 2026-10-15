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
