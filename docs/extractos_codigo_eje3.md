# Extractos de código relevantes del Eje 3

## 1. Propósito

Este documento presenta fragmentos breves del código que respaldan los requisitos centrales de la tercera entrega. Los extractos no sustituyen el repositorio: se incluyen para explicar la relación entre la regla de negocio, la implementación en Django, la persistencia en MySQL 8.4 y los casos CP-01 a CP-10.

> Antes de generar el PDF definitivo, verifique los números de línea contra la etiqueta final de la entrega. El código puede desplazarse si se modifica el archivo.

## 2. Mapa de trazabilidad técnica

| Requisito | Archivo principal | Elemento |
|---|---|---|
| Un voto por usuario, edición y categoría | `elecciones/models.py` | Campos y `UniqueConstraint` de `Participacion` |
| Migración de datos existentes | `elecciones/migrations/0006_unicidad_usuario_edicion_categoria.py` | `RunPython` y restricción |
| Validación de coherencia | `elecciones/models.py` | `Participacion.clean()` y `save()` |
| Confirmación transaccional | `elecciones/views.py` | `confirmar_voto()` |
| Rechazo anticipado de duplicidad | `elecciones/views.py` | `participar()` |
| Rechazo de opción ajena | `elecciones/forms.py` y `elecciones/views.py` | Queryset controlado y búsqueda relacionada |
| Historial privado | `elecciones/views.py` | `mis_participaciones()` |
| Concurrencia | `elecciones/test_eje3_concurrencia.py` | `TransactionTestCase`, hilos y barrera |
| API pública | `elecciones/views.py` y `elecciones/urls.py` | `api_categorias()` y ruta |
| Casos CP-01 a CP-08 | `elecciones/test_eje3_votacion_categoria.py` | Pruebas funcionales y de persistencia |
| CP-10 | `elecciones/test_eje3_api_categorias.py` | Pruebas de contrato y filtrado |

## 3. Participación asociada con edición y categoría

**Archivo:** `elecciones/models.py`.

```python
class Participacion(models.Model):
    votacion = models.ForeignKey(
        Votacion,
        on_delete=models.PROTECT,
        related_name="participaciones",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="participaciones",
    )
    edicion = models.ForeignKey(
        Edicion,
        on_delete=models.PROTECT,
        related_name="participaciones",
    )
    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="participaciones",
        null=True,
        blank=True,
    )
```

**Explicación:** la participación conserva la votación concreta y también la categoría y edición que determinan el derecho de voto. La asociación explícita permite que MySQL aplique una restricción única sin depender de relaciones atravesadas entre tablas.

**Requisitos relacionados:** CP-01, CP-02, CP-03, CP-07 y CP-08.

## 4. Restricción única en MySQL

**Archivo:** `elecciones/models.py`.

```python
models.UniqueConstraint(
    fields=["usuario", "edicion", "categoria"],
    name=(
        "una_participacion_por_"
        "usuario_edicion_categoria"
    ),
)
```

**Explicación:** esta restricción impide que la base acepte una segunda participación para la misma combinación de usuario, edición y categoría. La regla también protege solicitudes simultáneas, porque la decisión final no depende únicamente de una consulta previa en la vista.

Los registros históricos con `usuario=None` se conservan. MySQL permite múltiples valores nulos dentro de un índice único, por lo que esas participaciones no colisionan entre sí.

**Requisitos relacionados:** CP-02 y CP-09.

## 5. Validación de coherencia de la participación

**Archivo:** `elecciones/models.py`.

```python
def clean(self):
    errors = {}

    if self.votacion_id:
        categoria_esperada_id = self.votacion.categoria_id
        edicion_esperada_id = self.votacion.categoria.edicion_id

        if (
            self.categoria_id
            and self.categoria_id != categoria_esperada_id
        ):
            errors["categoria"] = (
                "La categoría no corresponde a la votación."
            )

        if (
            self.edicion_id
            and self.edicion_id != edicion_esperada_id
        ):
            errors["edicion"] = (
                "La edición no corresponde a la votación."
            )

    if errors:
        raise ValidationError(errors)
```

**Explicación:** como categoría y edición se almacenan de manera explícita, el modelo comprueba que ambos valores correspondan con la votación. Esta defensa evita registros desnormalizados o inconsistentes.

**Requisitos relacionados:** CP-01, CP-06 y CP-08.

## 6. Asignación automática y validación antes de guardar

**Archivo:** `elecciones/models.py`.

```python
def save(self, *args, **kwargs):
    if self.votacion_id:
        if not self.categoria_id:
            self.categoria_id = self.votacion.categoria_id

        if not self.edicion_id:
            self.edicion_id = (
                self.votacion.categoria.edicion_id
            )

    self.full_clean()
    return super().save(*args, **kwargs)
```

**Explicación:** el método completa los campos cuando se crean participaciones desde código heredado o pruebas anteriores y ejecuta las validaciones del modelo antes de persistir. La vista principal también asigna los campos expresamente para hacer visible la regla de negocio.

## 7. Migración segura de registros existentes

**Archivo:** `elecciones/migrations/0006_unicidad_usuario_edicion_categoria.py`.

```python
def completar_categoria_y_edicion(apps, schema_editor):
    Participacion = apps.get_model(
        "elecciones",
        "Participacion",
    )

    participaciones = Participacion.objects.select_related(
        "votacion__categoria__edicion"
    ).all()

    for participacion in participaciones.iterator():
        categoria = participacion.votacion.categoria
        participacion.categoria_id = categoria.pk
        participacion.edicion_id = categoria.edicion_id
        participacion.save(
            update_fields=["categoria", "edicion"]
        )
```

**Explicación:** la migración agrega inicialmente los campos como anulables, completa los datos de las participaciones existentes desde la votación y después los convierte en obligatorios. Este orden evita perder los registros históricos de la base principal.

La migración termina creando `una_participacion_por_usuario_edicion_categoria`.

**Requisitos relacionados:** CP-02, CP-08 y CP-09.

## 8. Validación anticipada de voto repetido

**Archivo:** `elecciones/views.py`, función `participar()`.

```python
if Participacion.objects.filter(
    usuario=request.user,
    edicion=votacion.categoria.edicion,
    categoria=votacion.categoria,
    estado=Participacion.Estado.CONFIRMADA,
).exists():
    messages.warning(
        request,
        (
            "Esta cuenta ya registró una participación "
            "en esta categoría para la edición actual."
        ),
    )
    return redirect(
        "elecciones:participacion_duplicada",
        slug=slug,
    )
```

**Explicación:** la vista ofrece una respuesta comprensible antes de llegar a la base de datos. La consulta utiliza categoría y edición, no solo la votación actual, por lo que también bloquea otro subevento de la misma categoría.

**Requisito relacionado:** CP-02.

## 9. Confirmación transaccional del voto

**Archivo:** `elecciones/views.py`, función `confirmar_voto()`.

```python
try:
    with transaction.atomic():
        participacion = Participacion.objects.create(
            votacion=votacion,
            categoria=votacion.categoria,
            edicion=votacion.categoria.edicion,
            usuario=request.user,
            referencia=(
                f"VOT-{timezone.now():%Y%m%d}-"
                f"{secrets.token_hex(4).upper()}"
            ),
            clave_sesion=clave_sesion,
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        voto = Voto(
            participacion=participacion,
            votacion=votacion,
            opcion=opcion,
        )
        voto.full_clean()
        voto.save()
except IntegrityError:
    return redirect(
        "elecciones:participacion_duplicada",
        slug=slug,
    )
```

**Explicación:** `transaction.atomic()` agrupa participación y voto en una sola operación. Si ocurre una violación de integridad, la transacción se revierte y el sistema dirige al usuario a la página de participación duplicada. Así se evita una participación sin voto o un voto incompleto.

**Requisitos relacionados:** CP-01, CP-02, CP-08 y CP-09.

## 10. Opción limitada a la votación actual

**Archivo:** `elecciones/forms.py`, formulario `SeleccionVotoForm`.

```python
class SeleccionVotoForm(forms.Form):
    opcion = forms.ModelChoiceField(
        queryset=Opcion.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
    )

    def __init__(self, *args, votacion, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opcion"].queryset = (
            votacion.opciones.filter(activa=True)
        )
```

**Archivo:** `elecciones/views.py`.

```python
opcion = get_object_or_404(
    votacion.opciones,
    pk=opcion_id,
    activa=True,
)
```

**Explicación:** el formulario solo acepta opciones activas vinculadas con la votación. La vista vuelve a validar la relación al revisar y confirmar. Un identificador manipulado de otra categoría no supera el control del servidor.

**Requisito relacionado:** CP-06.

> Verifique el nombre y la ubicación exacta de `SeleccionVotoForm` antes del PDF final. El comportamiento está cubierto por `test_cp06_opcion_de_otra_categoria_es_rechazada`.

## 11. Historial privado del usuario

**Archivo:** `elecciones/views.py`, función `mis_participaciones()`.

```python
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
    .order_by("-confirmada_en", "-iniciada_en")
)
```

**Explicación:** la consulta filtra por el usuario autenticado y por participaciones confirmadas. `select_related()` recupera la información de votación, categoría, edición y tipo en una consulta eficiente. La plantilla no revela la opción seleccionada.

**Requisito relacionado:** CP-07.

## 12. Protección frente a concurrencia

**Archivo:** `elecciones/test_eje3_concurrencia.py`.

```python
class ConcurrenciaEje3Tests(TransactionTestCase):
    reset_sequences = True

    def test_cp09_dos_intentos_simultaneos_registran_un_voto(
        self,
    ):
        barrera = Barrier(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [
                executor.submit(
                    self._registrar_intento,
                    *argumento,
                )
                for argumento in argumentos
            ]
            resultados = [
                futuro.result(timeout=20)
                for futuro in futuros
            ]
```

La función ejecutada por cada hilo utiliza conexiones separadas y una transacción:

```python
close_old_connections()
barrera.wait(timeout=10)

with transaction.atomic():
    participacion = Participacion.objects.create(...)
    voto = Voto(...)
    voto.full_clean()
    voto.save()
```

Las afirmaciones finales exigen:

```python
self.assertEqual(resultados.count("registrado"), 1)
self.assertEqual(participaciones.count(), 1)
self.assertEqual(votos.count(), 1)
```

**Explicación:** `TransactionTestCase` permite observar transacciones reales. `ThreadPoolExecutor` inicia dos intentos, `Barrier` sincroniza el instante de escritura y `close_old_connections()` impide compartir una conexión entre hilos. La prueba demuestra que solo queda una participación y un voto.

**Requisito relacionado:** CP-09.

## 13. API pública de categorías

**Archivo:** `elecciones/views.py`, función `api_categorias()`.

```python
edicion = (
    Edicion.objects.filter(
        estado=Edicion.Estado.ACTIVA,
    )
    .order_by("-anio", "-pk")
    .first()
)

categorias = (
    Categoria.objects.filter(
        edicion=edicion,
        estado=EstadoBase.ACTIVO,
        visible_publicamente=True,
    )
    .prefetch_related(
        Prefetch(
            "votaciones",
            queryset=Votacion.objects.filter(
                publicada=True,
            ).exclude(
                estado=Votacion.Estado.CANCELADA,
            ),
        )
    )
)
```

La respuesta se construye con `JsonResponse`:

```python
return JsonResponse(
    {
        "edicion": {
            "id": edicion.pk,
            "nombre": edicion.nombre,
            "anio": edicion.anio,
        },
        "categorias": datos_categorias,
    }
)
```

**Explicación:** la consulta incluye la edición activa, categorías activas y visibles, votaciones publicadas no canceladas y opciones activas. `Prefetch` reduce consultas repetidas. La respuesta no incluye usuarios, participaciones o votos individuales.

**Requisito relacionado:** CP-10.

## 14. Ruta GET de la API

**Archivo:** `elecciones/urls.py`.

```python
path(
    "api/categorias/",
    views.api_categorias,
    name="api_categorias",
)
```

La vista rechaza métodos distintos de GET:

```python
if request.method != "GET":
    return HttpResponseNotAllowed(["GET"])
```

**Explicación:** el contrato es de solo lectura. Una solicitud POST recibe HTTP 405 y no altera la base de datos.

**Requisito relacionado:** CP-10.

## 15. Prueba de voto válido y persistencia

**Archivo:** `elecciones/test_eje3_votacion_categoria.py`.

```python
def test_cp01_voto_valido_se_registra_en_mysql(self):
    self.client.force_login(self.usuario)
    self.emitir_voto(self.votacion_uno, self.opcion_uno)

    participacion = Participacion.objects.get(
        usuario=self.usuario,
        categoria=self.categoria_uno,
        edicion=self.edicion,
    )

    self.assertTrue(
        Voto.objects.filter(
            participacion=participacion,
            votacion=self.votacion_uno,
            opcion=self.opcion_uno,
        ).exists()
    )
```

**Explicación:** la prueba recorre el flujo web y después consulta el ORM para comprobar que participación y voto fueron persistidos con las relaciones esperadas.

**Requisitos relacionados:** CP-01 y CP-08.

## 16. Segundo subevento de la misma categoría

**Archivo:** `elecciones/test_eje3_votacion_categoria.py`.

```python
def test_cp02_no_permite_segundo_voto_en_misma_categoria(
    self,
):
    self.emitir_voto(self.votacion_uno, self.opcion_uno)

    response = self.client.get(
        reverse(
            "elecciones:participar",
            kwargs={"slug": self.votacion_dos.slug},
        )
    )

    self.assertEqual(
        Participacion.objects.filter(
            usuario=self.usuario,
            categoria=self.categoria_uno,
            edicion=self.edicion,
        ).count(),
        1,
    )
```

**Explicación:** las dos votaciones pertenecen a la misma categoría. El segundo acceso es rechazado y la base conserva una sola participación.

**Requisito relacionado:** CP-02.

## 17. Pruebas del contrato de la API

**Archivo:** `elecciones/test_eje3_api_categorias.py`.

```python
def test_cp10_get_devuelve_json_valido(self):
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(
        response["Content-Type"],
        "application/json",
    )

    datos = response.json()
    self.assertIn("edicion", datos)
    self.assertIn("categorias", datos)
```

Otras pruebas verifican:

- selección de la edición activa;
- inclusión de categorías y opciones reales;
- exclusión de categorías ocultas, votaciones no publicadas y opciones inactivas;
- ausencia de datos sensibles;
- respuesta vacía cuando no existe edición activa;
- rechazo HTTP 405 para métodos distintos de GET.

**Requisito relacionado:** CP-10.

## 18. Comandos de validación

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate --plan
python manage.py test elecciones.test_eje3_votacion_categoria -v 2
python manage.py test elecciones.test_eje3_concurrencia -v 2
python manage.py test elecciones.test_eje3_api_categorias -v 2
python manage.py test -v 2
```

Resultado de referencia:

```text
Found 114 test(s).
Ran 114 tests
OK
```

## 19. Selección recomendada para el PDF

Para mantener el documento académico legible, incluir únicamente estos extractos principales:

1. Restricción `usuario + edición + categoría`.
2. Migración de datos existentes.
3. Confirmación con `transaction.atomic()`.
4. Validación de opción relacionada.
5. Prueba concurrente.
6. Consulta y respuesta de la API.
7. Una prueba funcional CP-01 o CP-02.

Cada fragmento debe acompañarse de:

- archivo y elemento de origen;
- requisito relacionado;
- explicación de dos a cuatro párrafos;
- evidencia funcional o prueba automatizada;
- resultado obtenido.

No se recomienda reproducir archivos completos en el PDF.

## 20. Verificación antes del cierre

- [ ] Los fragmentos coinciden con la etiqueta final del repositorio.
- [ ] Los números de línea fueron actualizados después del último cambio.
- [ ] No se incluyeron secretos, contraseñas o datos personales.
- [ ] Cada extracto está relacionado con un caso CP.
- [ ] La explicación distingue validación de aplicación y restricción de base de datos.
- [ ] La prueba CP-09 se ejecutó sobre MySQL, no SQLite.
- [ ] La API se presentó como GET de solo lectura.
- [ ] El PDF contiene fragmentos breves, no archivos completos.
