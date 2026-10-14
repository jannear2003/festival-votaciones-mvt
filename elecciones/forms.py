from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Categoria, Edicion, EstadoBase

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["edicion", "nombre", "descripcion", "reglas", "orden", "estado", "visible_publicamente"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3}), "reglas": forms.Textarea(attrs={"rows": 4})}
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("visible_publicamente") and cleaned.get("estado") != EstadoBase.ACTIVO:
            self.add_error("visible_publicamente", "Solo una categoría activa puede ser visible públicamente.")
        return cleaned

class CopiarCategoriasForm(forms.Form):
    edicion_origen = forms.ModelChoiceField(queryset=Edicion.objects.none(), label="Edición de origen")
    edicion_destino = forms.ModelChoiceField(queryset=Edicion.objects.none(), label="Edición de destino")
    categorias = forms.ModelMultipleChoiceField(queryset=Categoria.objects.none(), widget=forms.CheckboxSelectMultiple, label="Categorías que se copiarán", help_text="Las copias quedarán en Borrador y no visibles.")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["edicion_origen"].queryset = Edicion.objects.select_related("festival").all()
        self.fields["edicion_destino"].queryset = Edicion.objects.select_related("festival").all()
        origen = self.data.get("edicion_origen") or self.initial.get("edicion_origen")
        if origen:
            self.fields["categorias"].queryset = Categoria.objects.filter(edicion_id=origen).order_by("orden", "nombre")
    def clean(self):
        cleaned = super().clean(); origen = cleaned.get("edicion_origen"); destino = cleaned.get("edicion_destino"); categorias = cleaned.get("categorias")
        if origen and destino and origen.pk == destino.pk:
            self.add_error("edicion_destino", "La edición de destino debe ser diferente.")
        if origen and categorias and categorias.exclude(edicion=origen).exists():
            raise ValidationError("Todas las categorías deben pertenecer a la edición de origen.")
        return cleaned
    @transaction.atomic
    def copiar(self):
        destino = self.cleaned_data["edicion_destino"]; creadas = []; omitidas = []
        for categoria in self.cleaned_data["categorias"]:
            copia, creada = Categoria.objects.get_or_create(edicion=destino, nombre=categoria.nombre, defaults={"descripcion": categoria.descripcion, "reglas": categoria.reglas, "orden": categoria.orden, "estado": EstadoBase.BORRADOR, "visible_publicamente": False})
            (creadas if creada else omitidas).append(copia)
        return creadas, omitidas

from django.forms import inlineformset_factory
from django.utils.text import slugify
from .models import Opcion, TipoVotacion, Votacion


class VotacionForm(forms.ModelForm):
    class Meta:
        model = Votacion
        fields = [
            "categoria", "tipo", "nombre", "slug", "descripcion",
            "fecha_apertura", "fecha_cierre", "estado", "publicada",
            "resultados_publicos",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "fecha_apertura": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "fecha_cierre": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_apertura"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["fecha_cierre"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["categoria"].queryset = Categoria.objects.select_related("edicion").exclude(estado=EstadoBase.ARCHIVADO)
        self.fields["tipo"].queryset = TipoVotacion.objects.filter(activo=True)
        if self.instance and self.instance.pk:
            self.fields["fecha_apertura"].initial = self.instance.fecha_apertura.strftime("%Y-%m-%dT%H:%M")
            self.fields["fecha_cierre"].initial = self.instance.fecha_cierre.strftime("%Y-%m-%dT%H:%M")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or slugify(self.cleaned_data.get("nombre", ""))
        if not slug:
            raise ValidationError("Ingrese un identificador URL válido.")
        return slug

    def clean(self):
        cleaned = super().clean()
        apertura, cierre = cleaned.get("fecha_apertura"), cleaned.get("fecha_cierre")
        publicada, estado = cleaned.get("publicada"), cleaned.get("estado")
        categoria = cleaned.get("categoria")
        if apertura and cierre and cierre <= apertura:
            self.add_error("fecha_cierre", "El cierre debe ser posterior a la apertura.")
        if publicada and estado == Votacion.Estado.BORRADOR:
            self.add_error("publicada", "Una votación en borrador no puede publicarse.")
        if publicada and categoria and (categoria.estado != EstadoBase.ACTIVO or not categoria.visible_publicamente):
            self.add_error("publicada", "La categoría debe estar activa y visible antes de publicar.")
        return cleaned


class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ["nombre", "descripcion", "orden", "activa"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 2})}


OpcionFormSet = inlineformset_factory(
    Votacion,
    Opcion,
    form=OpcionForm,
    extra=1,
    can_delete=True,
    min_num=2,
    validate_min=True,
)

class SeleccionVotoForm(forms.Form):
    opcion = forms.ModelChoiceField(queryset=Opcion.objects.none(), widget=forms.RadioSelect, empty_label=None, label="Seleccione una opción")

    def __init__(self, *args, votacion=None, **kwargs):
        super().__init__(*args, **kwargs)
        if votacion is not None:
            self.fields["opcion"].queryset = votacion.opciones.filter(activa=True).order_by("orden", "nombre")
