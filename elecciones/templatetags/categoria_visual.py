from django import template

register = template.Library()

@register.filter
def categoria_imagen(categoria):
    texto = f"{getattr(categoria, 'nombre', '')} {getattr(categoria, 'descripcion', '')}".lower()
    if any(p in texto for p in ("cancion", "canción", "composicion", "composición", "inedita", "inédita")):
        return "images/categories/categoria-cancion.webp"
    if any(p in texto for p in ("juvenil", "joven", "infantil", "menor")):
        return "images/categories/categoria-juvenil.webp"
    return "images/categories/categoria-acordeon.webp"
