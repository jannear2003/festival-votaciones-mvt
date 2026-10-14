from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from .models import Categoria, Edicion, Votacion


def inicio(request):
    edicion = Edicion.objects.filter(estado=Edicion.Estado.ACTIVA).order_by("-anio").first()
    votaciones = Votacion.objects.none()
    if edicion:
        votaciones = (
            Votacion.objects.filter(
                categoria__edicion=edicion,
                categoria__estado="ACTIVO",
                categoria__visible_publicamente=True,
                publicada=True,
            )
            .select_related("categoria", "tipo")
            .annotate(total_opciones=Count("opciones", filter=Q(opciones__activa=True)))
        )
    return render(request, "elecciones/inicio.html", {"edicion": edicion, "votaciones": votaciones})


def detalle(request, slug):
    votacion = get_object_or_404(
        Votacion.objects.select_related("categoria", "categoria__edicion", "tipo").prefetch_related("opciones"),
        slug=slug,
        publicada=True,
        categoria__visible_publicamente=True,
    )
    return render(request, "elecciones/detalle.html", {"votacion": votacion})


@login_required
def panel(request):
    contexto = {
        "ediciones": Edicion.objects.count(),
        "categorias": Categoria.objects.count(),
        "votaciones": Votacion.objects.count(),
        "publicadas": Votacion.objects.filter(publicada=True).count(),
        "ultimas": Votacion.objects.select_related("categoria", "categoria__edicion")[:5],
    }
    return render(request, "elecciones/panel.html", contexto)
