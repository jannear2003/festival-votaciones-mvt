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
