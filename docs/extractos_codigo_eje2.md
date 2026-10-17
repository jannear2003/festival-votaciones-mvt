# Extractos de código relevantes - Actividad evaluativa Eje 2

## Propósito

Este inventario selecciona fragmentos breves que pueden incorporarse al documento académico. Cada fragmento se vincula con un requisito, una evidencia funcional y una prueba. Las líneas indicadas corresponden al estado actual de la rama `actividad-eje2-mysql` y deben actualizarse si el código cambia.

## Criterios editoriales

- No incluir archivos completos.
- Limitar cada bloque a las líneas indispensables.
- Omitir contraseñas, tokens y valores de archivos `.env`.
- Explicar el propósito, no solo describir la sintaxis.
- Vincular código, evidencia visual y prueba automatizada.
- Revisar la numeración antes de llevar los fragmentos al PDF.

## Código 1. Configuración de MySQL

- **Archivo:** `config/settings.py`
- **Líneas de referencia:** 153-195
- **Requisito relacionado:** C1.3 Conexión MySQL
- **Explicación:** Evidencia la conexión parametrizada con MySQL, el uso de variables externas, utf8mb4 y comprobación de conexiones.
- **Evidencia asociada:** Captura del diagnóstico de conexión y del contenedor saludable.
- **Prueba asociada:** Ejecución de la suite sobre test_festival_votaciones.

```python
elif DB_ENGINE == "mysql":
    required_database_variables = (
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
    )

    missing_database_variables = [
        variable
        for variable in required_database_variables
        if not os.getenv(variable)
    ]

    if missing_database_variables:
        raise RuntimeError(
            "Faltan variables obligatorias de MySQL: "
            + ", ".join(missing_database_variables)
        )

    DATABASES = {
        "default": {
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 2. Modelo Edición

- **Archivo:** `elecciones/models.py`
- **Líneas de referencia:** 28-55
- **Requisito relacionado:** C1.5 Edición
- **Explicación:** Representa una edición anual y su relación con el Festival.
- **Evidencia asociada:** Captura de los registros relacionados en Django Admin.
- **Prueba asociada:** Pruebas de modelos y relaciones existentes.

```python
class Edicion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        CONFIGURACION = "CONFIGURACION", "En configuración"
        ACTIVA = "ACTIVA", "Activa"
        CERRADA = "CERRADA", "Cerrada"
        ARCHIVADA = "ARCHIVADA", "Archivada"

    festival = models.ForeignKey(Festival, on_delete=models.PROTECT, related_name="ediciones")
    nombre = models.CharField(max_length=150)
    anio = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)

    class Meta:
        verbose_name = "edición"
        verbose_name_plural = "ediciones"
        ordering = ["-anio", "nombre"]
        constraints = [models.UniqueConstraint(fields=["festival", "anio"], name="edicion_unica_por_festival_anio")]

# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 3. Modelo Categoría

- **Archivo:** `elecciones/models.py`
- **Líneas de referencia:** 58-82
- **Requisito relacionado:** C1.5 Edición a Categoría
- **Explicación:** Muestra la relación de cada categoría con una edición.
- **Evidencia asociada:** Captura de los registros relacionados en Django Admin.
- **Prueba asociada:** Pruebas de modelos y relaciones existentes.

```python
class Categoria(models.Model):
    edicion = models.ForeignKey(Edicion, on_delete=models.PROTECT, related_name="categorias")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    reglas = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=EstadoBase.choices, default=EstadoBase.BORRADOR)
    visible_publicamente = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["orden", "nombre"]
        constraints = [models.UniqueConstraint(fields=["edicion", "nombre"], name="categoria_nombre_unico_por_edicion")]

    def clean(self):
        if self.estado == EstadoBase.ACTIVO and self.edicion.estado not in {Edicion.Estado.CONFIGURACION, Edicion.Estado.ACTIVA}:
            raise ValidationError({"estado": "La categoría solo puede activarse en una edición en configuración o activa."})
        if self.visible_publicamente and self.estado != EstadoBase.ACTIVO:
            raise ValidationError({"visible_publicamente": "Solo una categoría activa puede ser visible públicamente."})
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 4. Modelo Votación

- **Archivo:** `elecciones/models.py`
- **Líneas de referencia:** 99-138
- **Requisito relacionado:** C1.6 Categoría a Votación
- **Explicación:** Muestra la relación de la votación con su categoría y sus reglas de estado.
- **Evidencia asociada:** Captura de los registros relacionados en Django Admin.
- **Prueba asociada:** Pruebas de modelos y relaciones existentes.

```python
class Votacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        PROGRAMADA = "PROGRAMADA", "Programada"
        ABIERTA = "ABIERTA", "Abierta"
        CERRADA = "CERRADA", "Cerrada"
        CANCELADA = "CANCELADA", "Cancelada"

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="votaciones")
    tipo = models.ForeignKey(TipoVotacion, on_delete=models.PROTECT, related_name="votaciones")
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    descripcion = models.TextField()
    fecha_apertura = models.DateTimeField()
    fecha_cierre = models.DateTimeField()
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR)
    publicada = models.BooleanField(default=False)
    resultados_publicos = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 5. Modelo Opción

- **Archivo:** `elecciones/models.py`
- **Líneas de referencia:** 141-156
- **Requisito relacionado:** C1.7 Votación a Opción
- **Explicación:** Muestra las opciones o participantes asociados con una votación.
- **Evidencia asociada:** Captura de los registros relacionados en Django Admin.
- **Prueba asociada:** Pruebas de modelos y relaciones existentes.

```python
class Opcion(models.Model):
    votacion = models.ForeignKey(Votacion, on_delete=models.PROTECT, related_name="opciones")
    nombre = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="opciones/", blank=True)
    orden = models.PositiveIntegerField(default=1)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "opción"
        verbose_name_plural = "opciones"
        ordering = ["orden", "nombre"]
        constraints = [models.UniqueConstraint(fields=["votacion", "nombre"], name="opcion_nombre_unico_por_votacion")]

    def __str__(self):
        return self.nombre
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 6. Formulario de registro de usuarios

- **Archivo:** `elecciones/forms.py`
- **Líneas de referencia:** 8-30
- **Requisito relacionado:** C2.1 Registro y C2.4 contraseñas seguras
- **Explicación:** Emplea UserCreationForm, conserva los validadores de Django y evita correos duplicados.
- **Evidencia asociada:** Captura del formulario de registro y sus validaciones.
- **Prueba asociada:** test_registro_valido_crea_usuario_y_redirige_al_login.

```python
class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Nombres")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Correo electronico")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "Ya existe una cuenta registrada con este correo."
            )
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 7. Vista de registro

- **Archivo:** `elecciones/views.py`
- **Líneas de referencia:** 45-64
- **Requisito relacionado:** C2.1 Registro
- **Explicación:** Procesa GET y POST, guarda la cuenta y redirige al inicio de sesión.
- **Evidencia asociada:** Registro satisfactorio y mensaje de confirmación.
- **Prueba asociada:** Pruebas de registro válido, duplicados y contraseñas diferentes.

```python
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
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 8. Login con redirección por rol

- **Archivo:** `elecciones/views.py`
- **Líneas de referencia:** 11-36
- **Requisito relacionado:** C2.2 Login
- **Explicación:** Diferencia cuentas públicas y administrativas después del inicio de sesión, sin debilitar la autorización.
- **Evidencia asociada:** Cuenta pública en el portal y cuenta administrativa en el panel.
- **Prueba asociada:** Pruebas de redirección por rol y parámetro next.

```python
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
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 9. Middleware de autorización

- **Archivo:** `elecciones/middleware.py`
- **Líneas de referencia:** 6-67
- **Requisito relacionado:** C2.9 Autorización adicional
- **Explicación:** Protege el bloque administrativo mediante grupos y permisos específicos por ruta.
- **Evidencia asociada:** Pantalla 403 para una cuenta pública.
- **Prueba asociada:** Pruebas de panel, navegación y Django Admin.

```python
class RolePermissionMiddleware:
    """Protege el bloque administrativo con grupos y permisos de Django."""

    ADMINISTRATIVE_GROUPS = {
        "Administrador general",
        "Configurador",
        "Operador",
        "Publicador",
        "Auditor",
    }

    ROUTE_PERMISSIONS = {
        "elecciones:categorias_lista": "elecciones.view_categoria",
        "elecciones:categoria_crear": "elecciones.add_categoria",
        "elecciones:categoria_editar": "elecciones.change_categoria",
        "elecciones:categoria_estado": "elecciones.change_categoria",
        "elecciones:categorias_copiar": "elecciones.add_categoria",
        "elecciones:votaciones_lista": "elecciones.view_votacion",
        "elecciones:votacion_crear": "elecciones.add_votacion",
        "elecciones:votacion_editar": "elecciones.change_votacion",
        "elecciones:votacion_publicacion": "elecciones.publicar_votacion",
        "elecciones:votacion_estado": "elecciones.operar_votacion",
# ... fragmento abreviado ...
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 10. Administración de votaciones

- **Archivo:** `elecciones/admin.py`
- **Líneas de referencia:** 49-55
- **Requisito relacionado:** C2.7 Votaciones y C2.8 Opciones
- **Explicación:** Configura listados, filtros, búsqueda, relaciones y opciones en línea mediante Django Admin.
- **Evidencia asociada:** Captura de una votación con opciones en Django Admin.
- **Prueba asociada:** Creación y consulta de votaciones y opciones.

```python
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "tipo", "estado", "publicada", "fecha_apertura", "fecha_cierre")
    list_filter = ("estado", "publicada", "tipo", "categoria__edicion")
    search_fields = ("nombre", "categoria__nombre", "categoria__edicion__nombre")
    prepopulated_fields = {"slug": ("nombre",)}
    autocomplete_fields = ("categoria", "tipo")
    inlines = [OpcionInline]
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 11. Consulta dinámica del portal

- **Archivo:** `elecciones/views.py`
- **Líneas de referencia:** 39-43
- **Requisito relacionado:** C3.1 Portal dinámico y C3.2 datos no codificados
- **Explicación:** Obtiene la edición activa y las votaciones publicadas desde el ORM, evitando datos codificados en la plantilla.
- **Evidencia asociada:** Portal público con datos creados en MySQL.
- **Prueba asociada:** Respuesta del portal y contenido esperado.

```python
def inicio(request):
    edicion = Edicion.objects.filter(estado=Edicion.Estado.ACTIVA).order_by("-anio").first(); votaciones = Votacion.objects.none()
    if edicion:
        votaciones = Votacion.objects.filter(categoria__edicion=edicion, categoria__estado=EstadoBase.ACTIVO, categoria__visible_publicamente=True, publicada=True).select_related("categoria", "tipo").annotate(total_opciones=Count("opciones", filter=Q(opciones__activa=True)))
    return render(request, "elecciones/inicio.html", {"edicion": edicion, "votaciones": votaciones})
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 12. Renderizado dinámico en plantilla

- **Archivo:** `templates/elecciones/inicio.html`
- **Líneas de referencia:** 4-11
- **Requisito relacionado:** C3.1 Portal dinámico
- **Explicación:** Recorre el contexto enviado por la vista y representa las votaciones almacenadas en MySQL.
- **Evidencia asociada:** Tarjetas de votaciones en el portal.
- **Prueba asociada:** Cambio de datos en Admin reflejado en el portal.

```django
<section><h2>Votaciones disponibles</h2><div class="grid">{% for v in votaciones %}<article class="card vote-card">
{% with ruta_imagen=v.categoria|categoria_imagen %}
{% with ruta_imagen=v.categoria|categoria_imagen %}
<div class="vote-card__image">
  <img src="{% static ruta_imagen %}" alt="" loading="lazy" width="1200" height="800">
</div>
{% endwith %}
{% endwith %}<span class="badge">{{ v.get_estado_display }}</span><p class="category">{{ v.categoria.nombre }} · {{ v.tipo.nombre }}</p><h3>{{ v.nombre }}</h3><p>{{ v.descripcion|truncatewords:25 }}</p><p><strong>{{ v.total_opciones }}</strong> opciones disponibles</p><a class="btn" href="{{ v.get_absolute_url }}">Consultar</a></article>{% empty %}<div class="empty"><h3>No hay votaciones publicadas</h3><p>La administración puede configurar ediciones, categorías y votaciones sin modificar el código.</p></div>{% endfor %}</div></section>
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 13. Prueba automatizada

- **Archivo:** `elecciones/test_registro.py`
- **Líneas de referencia:** 27-36
- **Requisito relacionado:** C2.1 y C2.4
- **Explicación:** Comprueba creación, datos básicos y hash de contraseña.
- **Evidencia asociada:** Salida de la suite completa con 26 pruebas aprobadas.
- **Prueba asociada:** test_registro_valido_crea_usuario_y_redirige_al_login

```python
    def test_registro_valido_crea_usuario_y_redirige_al_login(self):
        response = self.client.post(self.url, self.datos_validos)
        self.assertRedirects(response, self.login_url)

        user = get_user_model().objects.get(username="usuario_nuevo")
        self.assertEqual(user.email, "usuario@example.com")
        self.assertEqual(user.first_name, "Usuario")
        self.assertEqual(user.last_name, "Academico")
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Código 14. Prueba automatizada

- **Archivo:** `elecciones/test_registro.py`
- **Líneas de referencia:** 105-114
- **Requisito relacionado:** C2.9
- **Explicación:** Comprueba que autenticarse no concede autorización administrativa.
- **Evidencia asociada:** Salida de la suite completa con 26 pruebas aprobadas.
- **Prueba asociada:** test_usuario_publico_no_accede_al_panel_administrativo

```python
    def test_usuario_publico_no_accede_al_panel_administrativo(self):
        user = get_user_model().objects.create_user(
            username="usuario_publico",
            email="publico@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("elecciones:panel"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
```

### Nota para el PDF

Redactar un párrafo que explique cómo el fragmento contribuye al flujo funcional y relacionarlo con la figura correspondiente.

## Control de incorporación al PDF

| Código | Revisado | Explicado | Figura vinculada | Prueba vinculada | Incorporado al PDF |
|---|---|---|---|---|---|
| Código 1 | No | No | No | Sí | No |
| Código 2 | No | No | No | Sí | No |
| Código 3 | No | No | No | Sí | No |
| Código 4 | No | No | No | Sí | No |
| Código 5 | No | No | No | Sí | No |
| Código 6 | No | No | No | Sí | No |
| Código 7 | No | No | No | Sí | No |
| Código 8 | No | No | No | Sí | No |
| Código 9 | No | No | No | Sí | No |
| Código 10 | No | No | No | Sí | No |
| Código 11 | No | No | No | Sí | No |
| Código 12 | No | No | No | Sí | No |
| Código 13 | No | No | No | Sí | No |
| Código 14 | No | No | No | Sí | No |
