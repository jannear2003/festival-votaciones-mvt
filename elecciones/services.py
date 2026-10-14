from django.db.models import Count
from .models import Opcion, Voto


def consolidar_resultados(votacion):
    total = Voto.objects.filter(votacion=votacion).count()
    opciones = (
        Opcion.objects.filter(votacion=votacion)
        .annotate(total_votos=Count("votos"))
        .order_by("orden", "nombre")
    )
    filas = []
    maximo = 0
    for opcion in opciones:
        cantidad = opcion.total_votos
        maximo = max(maximo, cantidad)
        filas.append({
            "opcion_id": opcion.pk,
            "nombre": opcion.nombre,
            "votos": cantidad,
            "porcentaje": round((cantidad * 100 / total), 2) if total else 0,
        })
    for fila in filas:
        fila["lider"] = bool(total and fila["votos"] == maximo)
    lideres = [fila["nombre"] for fila in filas if fila["lider"]]
    return {
        "total_votos": total,
        "opciones": filas,
        "empate": len(lideres) > 1 and total > 0,
        "lideres": lideres,
    }


def registrar_evento(request, accion, entidad, identificador, detalle=None):
    from .models import EventoAuditoria
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
    return EventoAuditoria.objects.create(
        usuario=request.user if getattr(request.user, "is_authenticated", False) else None,
        accion=accion,
        entidad=entidad,
        identificador=str(identificador),
        detalle=detalle or {},
        direccion_ip=ip,
    )
