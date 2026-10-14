from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import CategoriaForm, CopiarCategoriasForm
from .models import Categoria, Edicion, EstadoBase, Votacion

def inicio(request):
    edicion = Edicion.objects.filter(estado=Edicion.Estado.ACTIVA).order_by("-anio").first(); votaciones = Votacion.objects.none()
    if edicion:
        votaciones = Votacion.objects.filter(categoria__edicion=edicion, categoria__estado=EstadoBase.ACTIVO, categoria__visible_publicamente=True, publicada=True).select_related("categoria", "tipo").annotate(total_opciones=Count("opciones", filter=Q(opciones__activa=True)))
    return render(request, "elecciones/inicio.html", {"edicion": edicion, "votaciones": votaciones})

def detalle(request, slug):
    votacion = get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion", "tipo").prefetch_related("opciones"), slug=slug, publicada=True, categoria__visible_publicamente=True)
    return render(request, "elecciones/detalle.html", {"votacion": votacion})

@login_required
def panel(request):
    return render(request, "elecciones/panel.html", {"ediciones": Edicion.objects.count(), "categorias": Categoria.objects.count(), "votaciones": Votacion.objects.count(), "publicadas": Votacion.objects.filter(publicada=True).count(), "ultimas": Votacion.objects.select_related("categoria", "categoria__edicion")[:5]})

@login_required
def categorias_lista(request):
    categorias = Categoria.objects.select_related("edicion", "edicion__festival").annotate(total_votaciones=Count("votaciones")); q=request.GET.get("q","").strip(); edicion=request.GET.get("edicion","").strip(); estado=request.GET.get("estado","").strip()
    if q: categorias=categorias.filter(Q(nombre__icontains=q)|Q(descripcion__icontains=q)|Q(edicion__nombre__icontains=q))
    if edicion: categorias=categorias.filter(edicion_id=edicion)
    if estado: categorias=categorias.filter(estado=estado)
    return render(request,"elecciones/categorias_lista.html",{"categorias":categorias,"ediciones":Edicion.objects.all(),"estados":EstadoBase.choices,"filtros":{"q":q,"edicion":edicion,"estado":estado}})

@login_required
def categoria_crear(request):
    form=CategoriaForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        categoria=form.save(); messages.success(request,f"La categoría “{categoria.nombre}” fue creada correctamente."); return redirect("elecciones:categorias_lista")
    return render(request,"elecciones/categoria_form.html",{"form":form,"titulo":"Crear categoría"})

@login_required
def categoria_editar(request,pk):
    categoria=get_object_or_404(Categoria,pk=pk); form=CategoriaForm(request.POST or None,instance=categoria)
    if request.method=="POST" and form.is_valid():
        categoria=form.save(); messages.success(request,f"La categoría “{categoria.nombre}” fue actualizada."); return redirect("elecciones:categorias_lista")
    return render(request,"elecciones/categoria_form.html",{"form":form,"titulo":"Editar categoría","categoria":categoria})

@login_required
def categoria_estado(request,pk,accion):
    if request.method!="POST": return HttpResponseNotAllowed(["POST"])
    categoria=get_object_or_404(Categoria.objects.select_related("edicion"),pk=pk); destinos={"activar":EstadoBase.ACTIVO,"desactivar":EstadoBase.INACTIVO,"archivar":EstadoBase.ARCHIVADO}
    if accion not in destinos: messages.error(request,"La acción solicitada no es válida."); return redirect("elecciones:categorias_lista")
    categoria.estado=destinos[accion]
    if categoria.estado!=EstadoBase.ACTIVO: categoria.visible_publicamente=False
    try:
        categoria.full_clean(); categoria.save(update_fields=["estado","visible_publicamente","actualizado_en"]); messages.success(request,f"La categoría “{categoria.nombre}” ahora está {categoria.get_estado_display().lower()}.")
    except Exception as exc: messages.error(request,f"No fue posible cambiar el estado: {exc}")
    return redirect(request.POST.get("next") or reverse("elecciones:categorias_lista"))

@login_required
def categorias_copiar(request):
    form=CopiarCategoriasForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        creadas,omitidas=form.copiar()
        if creadas: messages.success(request,f"Se copiaron {len(creadas)} categoría(s) en estado borrador.")
        if omitidas: messages.warning(request,f"Se omitieron {len(omitidas)} categoría(s) porque ya existían en el destino.")
        return redirect("elecciones:categorias_lista")
    return render(request,"elecciones/categorias_copiar.html",{"form":form})
