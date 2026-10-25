from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Exists, OuterRef, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from .forms import CategoriaForm, CopiarCategoriasForm, RegistroUsuarioForm
from .models import Categoria, Edicion, EstadoBase, Votacion

class LoginPorRolView(LoginView):
    template_name = "registration/login.html"

    ADMINISTRATIVE_GROUPS = {
        "Administrador general",
        "Configurador",
        "Operador",
        "Publicador",
        "Auditor",
    }

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        user = self.request.user
        if (
            user.is_superuser
            or user.groups.filter(
                name__in=self.ADMINISTRATIVE_GROUPS
            ).exists()
        ):
            return reverse_lazy("elecciones:panel")

        return reverse_lazy("elecciones:inicio")


def inicio(request):
    edicion = (
        Edicion.objects
        .filter(estado=Edicion.Estado.ACTIVA)
        .order_by("-anio")
        .first()
    )
    votaciones = Votacion.objects.none()

    if edicion:
        publicaciones_activas = PublicacionResultado.objects.filter(
            votacion=OuterRef("pk"),
            activa=True,
        )

        votaciones = (
            Votacion.objects
            .filter(
                categoria__edicion=edicion,
                categoria__estado=EstadoBase.ACTIVO,
                categoria__visible_publicamente=True,
                publicada=True,
            )
            .select_related(
                "categoria",
                "tipo",
            )
            .annotate(
                total_opciones=Count(
                    "opciones",
                    filter=Q(opciones__activa=True),
                ),
                tiene_resultado_publicado=(
                    Q(resultados_publicos=True)
                    & Exists(publicaciones_activas)
                ),
            )
        )

    return render(
        request,
        "elecciones/inicio.html",
        {
            "edicion": edicion,
            "votaciones": votaciones,
        },
    )

def registrar_usuario(request):
    if request.user.is_authenticated:
        messages.info(request, "La sesion ya esta iniciada.")
        return redirect("elecciones:inicio")

    form = RegistroUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(
            request,
            f"La cuenta de {usuario.username} fue creada correctamente. "
            "Ya puede iniciar sesion.",
        )
        return redirect("login")

    return render(
        request,
        "registration/registro.html",
        {"form": form},
    )


def detalle(request, slug):
    votacion = get_object_or_404(
        Votacion.objects
        .select_related(
            "categoria",
            "categoria__edicion",
            "tipo",
        )
        .prefetch_related("opciones"),
        slug=slug,
        publicada=True,
        categoria__visible_publicamente=True,
    )

    tiene_resultado_publicado = (
        votacion.resultados_publicos
        and PublicacionResultado.objects.filter(
            votacion=votacion,
            activa=True,
        ).exists()
    )

    return render(
        request,
        "elecciones/detalle.html",
        {
            "votacion": votacion,
            "tiene_resultado_publicado": (
                tiene_resultado_publicado
            ),
        },
    )

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
    form=CategoriaForm(request.POST or None, request.FILES or None)
    if request.method=="POST" and form.is_valid():
        categoria=form.save(); messages.success(request,f"La categoría “{categoria.nombre}” fue creada correctamente."); return redirect("elecciones:categorias_lista")
    return render(request,"elecciones/categoria_form.html",{"form":form,"titulo":"Crear categoría"})

@login_required
def categoria_editar(request,pk):
    categoria=get_object_or_404(Categoria,pk=pk); form=CategoriaForm(request.POST or None,request.FILES or None,instance=categoria,)
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

from django.db import transaction
from .forms import OpcionFormSet, VotacionForm


@login_required
def votaciones_lista(request):
    votaciones = Votacion.objects.select_related("categoria", "categoria__edicion", "tipo").annotate(total_opciones=Count("opciones"))
    q = request.GET.get("q", "").strip(); edicion = request.GET.get("edicion", "").strip(); estado = request.GET.get("estado", "").strip(); publicada = request.GET.get("publicada", "").strip()
    if q:
        votaciones = votaciones.filter(Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q) | Q(tipo__nombre__icontains=q))
    if edicion:
        votaciones = votaciones.filter(categoria__edicion_id=edicion)
    if estado:
        votaciones = votaciones.filter(estado=estado)
    if publicada in {"si", "no"}:
        votaciones = votaciones.filter(publicada=publicada == "si")
    return render(request, "elecciones/votaciones_lista.html", {"votaciones": votaciones, "ediciones": Edicion.objects.all(), "estados": Votacion.Estado.choices, "filtros": {"q": q, "edicion": edicion, "estado": estado, "publicada": publicada}})


def _guardar_votacion(request, instancia=None):
    form = VotacionForm(request.POST or None, request.FILES or None, instance=instancia)
    formset = OpcionFormSet(request.POST or None, request.FILES or None, instance=instancia, prefix="opciones")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            votacion = form.save()
            formset.instance = votacion
            formset.save()
        messages.success(request, f"La votación “{votacion.nombre}” fue guardada correctamente.")
        return redirect("elecciones:votaciones_lista")
    return render(request, "elecciones/votacion_form.html", {"form": form, "formset": formset, "titulo": "Editar votación" if instancia else "Crear votación", "votacion": instancia})


@login_required
def votacion_crear(request):
    return _guardar_votacion(request)


@login_required
def votacion_editar(request, pk):
    return _guardar_votacion(request, get_object_or_404(Votacion, pk=pk))


@login_required
def votacion_publicacion(request, pk, accion):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    votacion = get_object_or_404(Votacion.objects.select_related("categoria"), pk=pk)
    if accion not in {"publicar", "retirar"}:
        messages.error(request, "La acción solicitada no es válida.")
        return redirect("elecciones:votaciones_lista")
    if accion == "publicar":
        votacion.publicada = True
        if votacion.estado == Votacion.Estado.BORRADOR:
            votacion.estado = Votacion.Estado.PROGRAMADA
    else:
        votacion.publicada = False
    try:
        votacion.full_clean()
        votacion.save(update_fields=["publicada", "estado", "actualizado_en"])
        messages.success(request, "La votación fue publicada." if votacion.publicada else "La votación fue retirada del portal público.")
    except Exception as exc:
        messages.error(request, f"No fue posible completar la operación: {exc}")
    return redirect("elecciones:votaciones_lista")


@login_required
def votacion_estado(request, pk, estado):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    estados_validos = {valor for valor, etiqueta in Votacion.Estado.choices}
    votacion = get_object_or_404(Votacion, pk=pk)
    if estado not in estados_validos:
        messages.error(request, "El estado solicitado no es válido.")
    else:
        votacion.estado = estado
        if estado in {Votacion.Estado.BORRADOR, Votacion.Estado.CANCELADA}:
            votacion.publicada = False
        try:
            votacion.full_clean(); votacion.save(update_fields=["estado", "publicada", "actualizado_en"])
            messages.success(request, f"La votación ahora está {votacion.get_estado_display().lower()}.")
        except Exception as exc:
            messages.error(request, f"No fue posible cambiar el estado: {exc}")
    return redirect("elecciones:votaciones_lista")

import secrets
from django.db import IntegrityError
from django.utils import timezone
from .forms import SeleccionVotoForm
from .models import Participacion, Voto


def _votacion_habilitada(slug):
    ahora = timezone.now()
    return get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion", "tipo").prefetch_related("opciones"), slug=slug, publicada=True, estado=Votacion.Estado.ABIERTA, categoria__estado=EstadoBase.ACTIVO, categoria__visible_publicamente=True, fecha_apertura__lte=ahora, fecha_cierre__gte=ahora)


def _asegurar_sesion(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@login_required
def participar(request, slug):
    # El 404 queda reservado para un slug que realmente no existe.
    votacion = get_object_or_404(
        Votacion.objects.select_related(
            "categoria",
            "categoria__edicion",
            "tipo",
        ),
        slug=slug,
    )
    ahora = timezone.now()

    motivo_no_disponible = None
    if not votacion.publicada:
        motivo_no_disponible = "NO_PUBLICADA"
    elif votacion.estado == Votacion.Estado.CANCELADA:
        motivo_no_disponible = "CANCELADA"
    elif votacion.categoria.estado != "ACTIVO":
        motivo_no_disponible = "CATEGORIA_INACTIVA"
    elif not votacion.categoria.visible_publicamente:
        motivo_no_disponible = "CATEGORIA_NO_VISIBLE"
    elif ahora < votacion.fecha_apertura:
        motivo_no_disponible = "NO_INICIADA"
    elif ahora > votacion.fecha_cierre:
        motivo_no_disponible = "FINALIZADA"
    elif votacion.estado != Votacion.Estado.ABIERTA:
        motivo_no_disponible = "NO_ABIERTA"

    if motivo_no_disponible:
        return render(
            request,
            "elecciones/votacion_no_disponible.html",
            {
                "votacion": votacion,
                "motivo": motivo_no_disponible,
                "ahora": ahora,
            },
            status=403,
        )

    if Participacion.objects.filter(
        votacion=votacion,
        usuario=request.user,
        estado=Participacion.Estado.CONFIRMADA,
    ).exists():
        messages.warning(
            request,
            "Esta cuenta ya registró una participación en la votación.",
        )
        return redirect(
            "elecciones:participacion_duplicada",
            slug=slug,
        )

    form = SeleccionVotoForm(request.POST or None, votacion=votacion)
    if request.method == "POST" and form.is_valid():
        request.session[f"seleccion_votacion_{votacion.pk}"] = (
            form.cleaned_data["opcion"].pk
        )
        return redirect("elecciones:revisar_voto", slug=slug)

    return render(
        request,
        "elecciones/participar.html",
        {"votacion": votacion, "form": form},
    )


@login_required
def revisar_voto(request, slug):
    votacion = _votacion_habilitada(slug)
    opcion_id = request.session.get(f"seleccion_votacion_{votacion.pk}")
    if not opcion_id:
        messages.info(request, "Seleccione una opción antes de revisar la participación.")
        return redirect("elecciones:participar", slug=slug)
    opcion = get_object_or_404(votacion.opciones, pk=opcion_id, activa=True)
    return render(request, "elecciones/revisar_voto.html", {"votacion": votacion, "opcion": opcion})


@login_required
def confirmar_voto(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    votacion = _votacion_habilitada(slug)
    opcion_id = request.session.get(f"seleccion_votacion_{votacion.pk}")
    opcion = get_object_or_404(votacion.opciones, pk=opcion_id, activa=True)
    clave_sesion = _asegurar_sesion(request)
    try:
        with transaction.atomic():
            participacion = Participacion.objects.create(
                votacion=votacion,
                usuario=request.user,
                referencia=(
                    f"VOT-{timezone.now():%Y%m%d}-"
                    f"{secrets.token_hex(4).upper()}"
                ),
                clave_sesion=clave_sesion,
                estado=Participacion.Estado.CONFIRMADA,
                confirmada_en=timezone.now(),
            )
            voto = Voto(participacion=participacion, votacion=votacion, opcion=opcion)
            voto.full_clean()
            voto.save()
    except IntegrityError:
        messages.warning(request, "Esta cuenta ya registró una participación en la votación.")
        return redirect("elecciones:participacion_duplicada", slug=slug)
    request.session.pop(f"seleccion_votacion_{votacion.pk}", None)
    request.session[f"referencia_votacion_{votacion.pk}"] = participacion.referencia
    return redirect("elecciones:comprobante_voto", slug=slug)


@login_required
def comprobante_voto(request, slug):
    votacion = get_object_or_404(Votacion, slug=slug)
    referencia = request.session.get(f"referencia_votacion_{votacion.pk}")
    if not referencia:
        return redirect("elecciones:detalle", slug=slug)
    participacion = get_object_or_404(
        Participacion,
        referencia=referencia,
        usuario=request.user,
    )
    return render(request, "elecciones/comprobante_voto.html", {"votacion": votacion, "participacion": participacion})


@login_required
def participacion_duplicada(request, slug):
    votacion = get_object_or_404(
        Votacion,
        slug=slug,
    )

    participacion = Participacion.objects.filter(
        votacion=votacion,
        usuario=request.user,
        estado=Participacion.Estado.CONFIRMADA,
    ).first()

    if participacion is None:
        return redirect(
            "elecciones:participar",
            slug=slug,
        )

    return render(
        request,
        "elecciones/participacion_duplicada.html",
        {
            "votacion": votacion,
            "participacion": participacion,
        },
        status=409,
    )

from django.db.models import Max
from .forms import PublicacionResultadoForm
from .models import EventoAuditoria, PublicacionResultado
from .services import consolidar_resultados, registrar_evento


@login_required
def resultados_lista(request):
    votaciones = Votacion.objects.select_related("categoria", "categoria__edicion", "tipo").annotate(
        total_votos=Count("votos"),
        total_publicaciones=Count("publicaciones_resultado", distinct=True),
    )
    q = request.GET.get("q", "").strip()
    edicion = request.GET.get("edicion", "").strip()
    estado = request.GET.get("estado", "").strip()
    if q:
        votaciones = votaciones.filter(Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q))
    if edicion:
        votaciones = votaciones.filter(categoria__edicion_id=edicion)
    if estado:
        votaciones = votaciones.filter(estado=estado)
    return render(request, "elecciones/resultados_lista.html", {
        "votaciones": votaciones,
        "ediciones": Edicion.objects.all(),
        "estados": Votacion.Estado.choices,
        "filtros": {"q": q, "edicion": edicion, "estado": estado},
    })


@login_required
def resultado_detalle_admin(request, pk):
    votacion = get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion", "tipo"), pk=pk)
    resumen = consolidar_resultados(votacion)
    publicacion = votacion.publicaciones_resultado.filter(activa=True).first()
    form = PublicacionResultadoForm()
    return render(request, "elecciones/resultado_detalle_admin.html", {
        "votacion": votacion,
        "resumen": resumen,
        "publicacion": publicacion,
        "form": form,
    })


@login_required
def publicar_resultado(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    votacion = get_object_or_404(Votacion.objects.select_related("categoria"), pk=pk)
    form = PublicacionResultadoForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Revise la observación ingresada.")
        return redirect("elecciones:resultado_detalle_admin", pk=pk)
    if votacion.estado != Votacion.Estado.CERRADA:
        messages.error(request, "Solo se pueden publicar resultados de una votación cerrada.")
        return redirect("elecciones:resultado_detalle_admin", pk=pk)
    if not votacion.resultados_publicos:
        messages.error(request, "Habilite la opción Resultados públicos en la configuración de la votación.")
        return redirect("elecciones:resultado_detalle_admin", pk=pk)
    resumen = consolidar_resultados(votacion)
    if resumen["total_votos"] == 0:
        messages.error(request, "No es posible publicar una votación sin votos registrados.")
        return redirect("elecciones:resultado_detalle_admin", pk=pk)
    with transaction.atomic():
        PublicacionResultado.objects.filter(votacion=votacion, activa=True).update(activa=False, retirada_en=timezone.now())
        ultima = PublicacionResultado.objects.filter(votacion=votacion).aggregate(maxima=Max("version"))["maxima"] or 0
        publicacion = PublicacionResultado.objects.create(
            votacion=votacion,
            version=ultima + 1,
            resumen=resumen,
            observacion=form.cleaned_data["observacion"],
            publicada_por=request.user,
            activa=True,
        )
        registrar_evento(request, "PUBLICAR_RESULTADOS", "Votacion", votacion.pk, {"version": publicacion.version, "total_votos": resumen["total_votos"]})
    messages.success(request, f"Resultados publicados en la versión {publicacion.version}.")
    return redirect("elecciones:resultado_detalle_admin", pk=pk)


@login_required
def retirar_resultado(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    votacion = get_object_or_404(Votacion, pk=pk)
    publicacion = votacion.publicaciones_resultado.filter(activa=True).first()
    if not publicacion:
        messages.warning(request, "La votación no tiene resultados públicos activos.")
    else:
        with transaction.atomic():
            publicacion.activa = False
            publicacion.retirada_en = timezone.now()
            publicacion.save(update_fields=["activa", "retirada_en"])
            registrar_evento(request, "RETIRAR_RESULTADOS", "Votacion", votacion.pk, {"version": publicacion.version})
        messages.success(request, "Los resultados fueron retirados del portal público.")
    return redirect("elecciones:resultado_detalle_admin", pk=pk)


def resultado_publico(request, slug):
    votacion = get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion", "tipo"), slug=slug, resultados_publicos=True)
    publicacion = get_object_or_404(PublicacionResultado, votacion=votacion, activa=True)
    return render(request, "elecciones/resultado_publico.html", {"votacion": votacion, "publicacion": publicacion, "resumen": publicacion.resumen})


@login_required
def auditoria_lista(request):
    eventos = EventoAuditoria.objects.select_related("usuario")[:200]
    return render(request, "elecciones/auditoria_lista.html", {"eventos": eventos})


@login_required
def mis_participaciones(request):
    participaciones = (
        Participacion.objects.filter(
            usuario=request.user,
            estado=Participacion.Estado.CONFIRMADA,
        )
        .select_related(
            "votacion",
            "votacion__categoria",
            "votacion__categoria__edicion",
            "votacion__tipo",
        )
        .order_by(
            "-confirmada_en",
            "-iniciada_en",
        )
    )

    return render(
        request,
        "elecciones/mis_participaciones.html",
        {
            "participaciones": participaciones,
        },
    )


@login_required
def comprobante_participacion(request, referencia):
    participacion = get_object_or_404(
        Participacion.objects.select_related(
            "votacion",
            "votacion__categoria",
            "votacion__categoria__edicion",
            "votacion__tipo",
        ),
        referencia=referencia,
        usuario=request.user,
        estado=Participacion.Estado.CONFIRMADA,
    )

    return render(
        request,
        "elecciones/comprobante_voto.html",
        {
            "votacion": participacion.votacion,
            "participacion": participacion,
            "desde_historial": True,
        },
    )
