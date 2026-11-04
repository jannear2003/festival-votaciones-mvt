# Ficha de acceso y verificación del Eje 3

> Esta ficha debe ubicarse inmediatamente después de la portada del PDF definitivo. Antes de entregar, reemplace todos los campos marcados como **PENDIENTE** y valide los enlaces en una ventana privada.

## 1. Identificación de la entrega

| Campo | Información |
|---|---|
| Proyecto | Sistema web de votaciones para el Festival de la Leyenda Vallenata |
| Actividad | Actividad evaluativa Eje No. 3 |
| Institución | Fundación Universitaria del Área Andina |
| Modalidad | Proyecto académico |
| Motor de base de datos | MySQL 8.4 |
| Framework | Django 6.0.5 |
| Versión de Python | Python 3.12 |
| Rama funcional | `develop` |
| Rama documental | `docs/entrega-eje3` |
| Versión estable anterior | `main` |
| Fecha de corte | **PENDIENTE: fecha definitiva de entrega** |

## 2. Integrantes

| Integrante | Identificación académica | Aporte principal |
|---|---|---|
| Luis David García Giraldo | **PENDIENTE** | **PENDIENTE: describir aporte real** |
| Derek Alexander Castillo Méndez | **PENDIENTE** | **PENDIENTE: describir aporte real** |
| Andrés Márquez | **PENDIENTE** | **PENDIENTE: describir aporte real** |
| Jorge Ernesto Annear Naranjo | **PENDIENTE** | **PENDIENTE: describir aporte real** |

Los aportes deben corresponder con el trabajo efectivamente realizado y coincidir con la sección de contribuciones del PDF.

## 3. Repositorio público

| Campo | Valor |
|---|---|
| Repositorio | `https://github.com/jannear2003/festival-votaciones-mvt` |
| Rama para revisar el Eje 3 | `develop` |
| Pull Requests funcionales | PR 13 y PR 14 |
| Commit de API y concurrencia | `468c2df` |
| Merge funcional más reciente | `0b26dfb` |
| Etiqueta definitiva | **PENDIENTE: crear únicamente al cerrar la entrega** |

### Verificación del repositorio

- [ ] El repositorio abre sin autenticación en una ventana privada.
- [ ] La rama `develop` contiene la migración `0006_unicidad_usuario_edicion_categoria.py`.
- [ ] La rama `develop` contiene las pruebas de CP-01 a CP-10.
- [ ] `main` permanece en la versión académica anterior hasta la aprobación final.
- [ ] El README explica instalación, configuración, pruebas, API y regla de unicidad.
- [ ] No existen archivos `.env`, contraseñas, tokens o secretos versionados.

## 4. Video de sustentación

| Campo | Valor |
|---|---|
| Enlace del video | **PENDIENTE: URL definitiva** |
| Plataforma | **PENDIENTE: OneDrive, YouTube no listado u otra plataforma autorizada** |
| Duración máxima | 8 minutos |
| Duración real | **PENDIENTE: mm:ss** |
| Fecha de validación | **PENDIENTE** |

### Verificación del video

- [ ] El enlace abre sin solicitar permisos adicionales.
- [ ] El audio es comprensible.
- [ ] La resolución permite leer terminal, interfaz y API.
- [ ] El video no supera ocho minutos.
- [ ] Se describen CP-01 a CP-10 o se relacionan con la tabla de minutos.
- [ ] No aparecen contraseñas, tokens, cookies o archivos `.env`.
- [ ] Los minutos registrados en el PDF coinciden con la versión final del video.

## 5. Acceso a la aplicación

### Entorno principal de demostración

| Campo | Valor |
|---|---|
| Tipo de entorno | GitHub Codespaces |
| URL del portal | **PENDIENTE: URL temporal del puerto 8000** |
| URL de acceso | **PENDIENTE: URL `/cuentas/login/`** |
| URL de registro | **PENDIENTE: URL `/cuentas/registro/`** |
| URL de Mis participaciones | **PENDIENTE: URL `/cuenta/participaciones/`** |
| URL de administración | **PENDIENTE: URL `/administracion/`** |
| URL de Django Admin | **PENDIENTE: URL `/admin/`** |
| URL de API | **PENDIENTE: URL `/api/categorias/`** |
| Vigencia del entorno | Temporal; depende del Codespace y de la visibilidad del puerto 8000 |

> La URL del Codespace puede cambiar o dejar de responder cuando el entorno se detiene. El repositorio y sus instrucciones constituyen el mecanismo permanente de reproducción.

### Cuentas de demostración

| Tipo de cuenta | Usuario | Contraseña | Uso |
|---|---|---|---|
| Cuenta pública A | **PENDIENTE** | **Entregar por canal autorizado, no incluir en repositorio público** | CP-01, CP-02, CP-03 y CP-07 |
| Cuenta pública B | **PENDIENTE** | **Entregar por canal autorizado, no incluir en repositorio público** | Separación entre usuarios |
| Cuenta administrativa | **PENDIENTE** | **Entregar por canal autorizado, no incluir en repositorio público** | CP-08 y administración |

### Reglas para credenciales

1. Utilizar exclusivamente cuentas de demostración sin datos personales reales.
2. No incluir contraseñas reutilizadas, institucionales o personales.
3. No almacenar contraseñas en GitHub, README, capturas o código fuente.
4. Si el PDF debe contener una clave por exigencia académica, usar una clave temporal y rotarla o eliminarla después de la evaluación.
5. Preferir la entrega de credenciales mediante el mecanismo privado habilitado por la institución.

## 6. Instalación reproducible

### Comandos principales

```bash
git clone https://github.com/jannear2003/festival-votaciones-mvt
cd festival-votaciones-mvt
git switch develop
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.mysql.example .env.mysql
```

Después de configurar las contraseñas locales en `.env.mysql`:

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml up -d
set -a
source .env.mysql
set +a
export DB_ENGINE=mysql
export DB_NAME="$MYSQL_DATABASE"
export DB_USER="$MYSQL_USER"
export DB_PASSWORD="$MYSQL_PASSWORD"
export DB_HOST=127.0.0.1
export DB_PORT=3306
python manage.py migrate
python manage.py loaddata datos_desarrollo
python manage.py configurar_roles
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Resultado esperado

- Contenedor `festival-mysql` en estado `healthy`.
- Django conectado al motor `mysql`.
- Migración `0006_unicidad_usuario_edicion_categoria` aplicada.
- Portal disponible en el puerto 8000.
- API disponible en `/api/categorias/`.

## 7. Validación técnica

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Configuración Django | `python manage.py check` | Sin problemas identificados |
| Cambios de modelo | `python manage.py makemigrations --check` | `No changes detected` |
| Migraciones pendientes | `python manage.py migrate --plan` | Sin operaciones pendientes |
| Suite completa | `python manage.py test -v 2` | 108 pruebas aprobadas |
| API | Abrir `/api/categorias/` | HTTP 200 y JSON válido |
| Restricción única | Introspección de MySQL | `usuario_id`, `edicion_id`, `categoria_id`; única |

## 8. Casos obligatorios

| Caso | Descripción | Evidencia principal | Minuto del video |
|---|---|---|---|
| CP-01 | Voto válido | `figura-04-cp01-voto-valido.png` | **PENDIENTE** |
| CP-02 | Segundo voto en la misma categoría | `figura-05-cp02-voto-duplicado.png` | **PENDIENTE** |
| CP-03 | Voto en categoría diferente | `figura-06-cp03-otra-categoria.png` | **PENDIENTE** |
| CP-04 | Autenticación obligatoria | `figura-07-cp04-autenticacion-obligatoria.png` | **PENDIENTE** |
| CP-05 | Categoría no habilitada | `figura-08-cp05-categoria-no-habilitada.png` | **PENDIENTE** |
| CP-06 | Opción ajena rechazada | `figura-09-cp06-opcion-ajena.png` | **PENDIENTE** |
| CP-07 | Mis participaciones | `figura-10-cp07-mis-participaciones.png` | **PENDIENTE** |
| CP-08 | Consulta administrativa | `figura-11-cp08-consulta-administrativa.png` | **PENDIENTE** |
| CP-09 | Concurrencia | `figura-12-cp09-concurrencia.png` | **PENDIENTE** |
| CP-10 | API de categorías | `figura-13-cp10-api-categorias.png` | **PENDIENTE** |

## 9. Consideraciones de seguridad y privacidad

- La entrega es un prototipo académico, no un sistema electoral certificado.
- La aplicación utiliza mecanismos de hash de Django para contraseñas.
- La API no expone usuarios, correos, contraseñas, claves de sesión, referencias de participación ni votos individuales.
- Los comprobantes no revelan públicamente la opción seleccionada.
- La evidencia debe utilizar datos controlados y cuentas de demostración.
- El acceso productivo requeriría HTTPS, gestión institucional de identidades, protección de secretos, supervisión, respaldo, recuperación y revisión jurídica.

## 10. Lista de cierre de la ficha

- [ ] Se reemplazaron todos los campos **PENDIENTE**.
- [ ] Los nombres de integrantes y aportes fueron confirmados.
- [ ] El repositorio fue probado en ventana privada.
- [ ] El video fue probado en ventana privada.
- [ ] La duración real del video no supera ocho minutos.
- [ ] Las credenciales de demostración se entregaron por un canal seguro.
- [ ] La URL temporal del Codespace fue validada o se indicó claramente su carácter temporal.
- [ ] La tabla CP-01 a CP-10 contiene los minutos definitivos.
- [ ] La ficha está ubicada inmediatamente después de la portada del PDF.
- [ ] La información coincide con README, repositorio, video y matriz de pruebas.
