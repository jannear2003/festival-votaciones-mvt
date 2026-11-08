# Sistema de votaciones configurable para el Festival de la Leyenda Vallenata

Aplicación web académica desarrollada con Python, Django y el patrón MVT para administrar ediciones, categorías, votaciones, opciones, participaciones, votos y resultados del Festival de la Leyenda Vallenata.

La implementación correspondiente al Eje 3 utiliza MySQL 8.4 como motor principal. El sistema garantiza un único voto por usuario, edición y categoría, incluso cuando una categoría contiene varias votaciones o subeventos. El proyecto conserva compatibilidad adicional con PostgreSQL y SQLite.

## Estado de las ramas

- `main`: versión académica estable anterior al Eje 3.
- `develop`: integración funcional del Eje 3 mediante los Pull Requests 13, 14 y 15.
- `docs/entrega-eje3`: código funcional integrado, documentación académica y evidencias del Eje 3.
- `feature/entrega-eje3`: rama utilizada para implementar CP-01 a CP-10.
- `feature/datos-demo-eje3`: rama utilizada para crear el comando de preparación de datos controlados.

La rama `main` debe permanecer sin los incrementos del Eje 3 hasta completar la revisión del código, las evidencias, el video y el PDF definitivo.

## Alcance académico

La cadena funcional principal es:

```text
Festival -> Edición -> Categoría -> Votación -> Opción
```

El alcance implementado incluye:

- Ediciones configurables por festival y año.
- Categorías dinámicas vinculadas con una edición.
- Tipos de votación configurables.
- Votaciones con fechas, estados y publicación controlada.
- Opciones o participantes asociados con cada votación.
- Imágenes configurables para categorías, votaciones y opciones.
- Portal público alimentado desde MySQL.
- Django Admin e interfaces administrativas propias.
- Registro, inicio y cierre de sesión.
- Recuperación segura de contraseña.
- Autorización mediante grupos y permisos de Django.
- Redirección posterior al inicio de sesión según el tipo de cuenta.
- Emisión de voto exclusiva para usuarios autenticados.
- Selección, revisión y confirmación antes del registro definitivo.
- Restricción de un voto por usuario, edición y categoría.
- Control de solicitudes duplicadas y concurrentes.
- Comprobante privado sin revelar la opción seleccionada.
- Historial personal en “Mis participaciones”.
- Consulta pública controlada de resultados.
- Eventos de auditoría.
- API pública `GET /api/categorias/`.
- Comando idempotente para preparar datos controlados del Eje 3.
- Pruebas automatizadas ejecutadas sobre MySQL.

Las pruebas de carga y el despliegue productivo se conservan como evolución futura.

## Regla de voto único

El sistema permite un único voto por:

```text
usuario + edición + categoría
```

La regla continúa aplicándose cuando una categoría contiene varias votaciones o subeventos. Después de confirmar un voto en uno de ellos, el usuario no puede registrar otro voto dentro de la misma categoría y edición. Sí puede participar en una categoría diferente.

La protección se aplica mediante:

1. Validación previa en las vistas de Django.
2. Asociación de la participación con usuario, edición y categoría.
3. Transacción atómica durante la confirmación.
4. Manejo de errores de integridad.
5. Restricción única en MySQL.
6. Prueba automatizada con dos intentos concurrentes.

La restricción de base de datos se denomina:

```text
una_participacion_por_usuario_edicion_categoria
```

## Flujo de votación

```text
Registro o inicio de sesión
        |
Consulta de votación y opciones
        |
Selección de una opción
        |
Revisión
        |
Confirmación
        |
Validaciones del servidor
        |
Registro transaccional en MySQL
        |
Comprobante y Mis participaciones
```

## Arquitectura MVT

- **Modelo:** define festivales, ediciones, categorías, votaciones, opciones, participaciones, votos, publicaciones de resultados y eventos de auditoría.
- **Vista:** consulta y procesa información, valida formularios y aplica reglas de negocio, autenticación y autorización.
- **Plantilla:** presenta el portal público, la autenticación, el flujo de voto, los comprobantes y la administración.

Flujo general:

```text
URL -> Vista -> Modelo/ORM -> MySQL -> Plantilla o JSON -> Respuesta HTTP
```

## Tecnologías

- Python 3.12.
- Django 6.0.5.
- MySQL 8.4.
- mysqlclient.
- Pillow.
- Docker y Docker Compose.
- HTML y CSS.
- Git y GitHub Codespaces.
- PostgreSQL, Gunicorn y WhiteNoise como capacidades adicionales.

## Requisitos previos

Ruta recomendada:

- GitHub Codespaces, o
- Python 3.12, Git, Docker Desktop y Docker Compose.

Las dependencias Python se registran en `requirements.txt`.

## Instalación recomendada con MySQL

### 1. Obtener el proyecto

```bash
git clone https://github.com/jannear2003/festival-votaciones-mvt
cd festival-votaciones-mvt
git switch docs/entrega-eje3
```

La rama `docs/entrega-eje3` contiene el código funcional integrado, la documentación académica y las evidencias del Eje 3. La rama `develop` contiene la integración funcional, mientras `main` conserva la versión académica anterior.

Cuando se publique la etiqueta final, la versión evaluable podrá seleccionarse mediante:

```bash
git checkout entrega-eje3-v1.0
```

### 2. Crear y activar un entorno virtual

Linux, macOS o Codespaces:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

El resultado esperado de `pip check` es:

```text
No broken requirements found.
```

### 4. Preparar las variables de MySQL

Linux, macOS o Codespaces:

```bash
cp .env.mysql.example .env.mysql
```

Windows PowerShell:

```powershell
Copy-Item .env.mysql.example .env.mysql
```

Edite `.env.mysql` y reemplace únicamente las contraseñas ficticias. No confirme este archivo en Git.

Estructura de referencia:

```text
MYSQL_DATABASE=festival_votaciones
MYSQL_USER=festival_app
MYSQL_PASSWORD=CAMBIE_ESTA_CONTRASENA
MYSQL_ROOT_PASSWORD=CAMBIE_ESTA_CONTRASENA_ROOT
```

### 5. Iniciar MySQL 8.4

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml up -d
docker compose --env-file .env.mysql -f compose.mysql.yml ps
```

El contenedor `festival-mysql` debe aparecer como `healthy`.

### 6. Configurar Django para MySQL

Linux, macOS o Codespaces:

```bash
set -a
source .env.mysql
set +a

export DB_ENGINE=mysql
export DB_NAME="$MYSQL_DATABASE"
export DB_USER="$MYSQL_USER"
export DB_PASSWORD="$MYSQL_PASSWORD"
export DB_HOST=127.0.0.1
export DB_PORT=3306
```

No muestre ni publique contraseñas.

Compruebe la conexión:

```bash
python manage.py shell -c "
from django.db import connection
connection.ensure_connection()
print('Motor:', connection.vendor)
print('Base:', connection.settings_dict['NAME'])
print('Usuario:', connection.settings_dict['USER'])
with connection.cursor() as cursor:
    cursor.execute('SELECT VERSION()')
    print('Versión MySQL:', cursor.fetchone()[0])
"
```

### 7. Aplicar migraciones

```bash
python manage.py migrate
```

La migración principal del Eje 3 es:

```text
elecciones.0006_unicidad_usuario_edicion_categoria
```

Verifique que no existan migraciones pendientes:

```bash
python manage.py showmigrations elecciones
python manage.py migrate --plan
```

### 8. Cargar datos de demostración y configurar roles

En una instalación nueva, primero cargue el fixture `datos_desarrollo` y después configure los grupos y permisos administrativos:

```bash
python manage.py loaddata datos_desarrollo
python manage.py configurar_roles
```

La carga del fixture `datos_desarrollo` es un requisito previo para ejecutar `preparar_demo_eje3`, porque crea el festival y la edición base que utiliza el comando.

El orden requerido en una base de datos nueva es:

```bash
python manage.py migrate
python manage.py loaddata datos_desarrollo
python manage.py configurar_roles
python manage.py preparar_demo_eje3
```

El resultado esperado de la carga del fixture es similar a:

```text
Installed 14 object(s) from 1 fixture(s)
```

La configuración de roles debe crear o actualizar los siguientes grupos:

```text
Administrador general
Configurador
Operador
Publicador
Auditor
```

El proyecto también contiene el comando:

```bash
python manage.py seed_demo
```

No combine `seed_demo` con `loaddata datos_desarrollo` sin revisar previamente los datos que crea cada alternativa.

### Preparar datos controlados del Eje 3

El proyecto incluye un comando idempotente para crear o actualizar las cuentas, categorías, votaciones y opciones necesarias para demostrar los casos CP-01 a CP-10.

Primero, defina las contraseñas como variables temporales de la terminal.

Linux, macOS o Codespaces:

```bash
read -s -p "Contraseña para cuentas públicas demo: " \
  DEMO_EJE3_PASSWORD_PUBLICA
echo
export DEMO_EJE3_PASSWORD_PUBLICA

read -s -p "Contraseña para cuenta administrativa demo: " \
  DEMO_EJE3_PASSWORD_ADMIN
echo
export DEMO_EJE3_PASSWORD_ADMIN
```

Compruebe únicamente que las variables estén cargadas, sin imprimir sus valores:

```bash
test -n "$DEMO_EJE3_PASSWORD_PUBLICA" \
  && echo "Clave pública cargada"

test -n "$DEMO_EJE3_PASSWORD_ADMIN" \
  && echo "Clave administrativa cargada"
```

Prepare los datos de demostración:

```bash
python manage.py preparar_demo_eje3
```

El comando crea o actualiza:

- `demo_eje3_a`, cuenta pública de demostración.
- `demo_eje3_b`, segunda cuenta pública.
- `demo_eje3_admin`, cuenta administrativa.
- Una categoría principal con dos subeventos.
- Una categoría alternativa.
- Una categoría no habilitada.
- Cuatro votaciones.
- Doce opciones ficticias.

El comando puede ejecutarse varias veces sin duplicar registros. También actualiza la vigencia de las votaciones habilitadas.

Antes de repetir una práctica o grabación, retire únicamente los votos y participaciones de las cuentas de demostración:

```bash
python manage.py preparar_demo_eje3 --reiniciar-votos
```

La opción `--reiniciar-votos` no elimina participaciones históricas ni votos pertenecientes a usuarios diferentes de `demo_eje3_*`.

Las contraseñas no deben almacenarse en el repositorio, el README, las evidencias, las capturas o el video.

### 9. Crear un superusuario

```bash
python manage.py createsuperuser
```

Este paso es opcional si se utilizará únicamente la cuenta administrativa creada por `preparar_demo_eje3`.

### 10. Ejecutar la aplicación

```bash
python manage.py runserver 0.0.0.0:8000
```

En una instalación local, abra:

```text
http://127.0.0.1:8000/
```

## Rutas principales

- Portal público: `http://127.0.0.1:8000/`
- Registro: `http://127.0.0.1:8000/cuentas/registro/`
- Inicio de sesión: `http://127.0.0.1:8000/cuentas/login/`
- Mis participaciones: `http://127.0.0.1:8000/cuenta/participaciones/`
- Panel propio: `http://127.0.0.1:8000/administracion/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- API de categorías: `http://127.0.0.1:8000/api/categorias/`

En GitHub Codespaces debe utilizarse la dirección asignada al puerto 8000.

## API pública de categorías

Endpoint:

```http
GET /api/categorias/
```

La respuesta JSON consulta datos reales de MySQL e incluye:

- Edición activa.
- Categorías activas y visibles públicamente.
- Votaciones publicadas y no canceladas.
- Opciones activas.

La API no expone usuarios, correos, contraseñas, claves de sesión, referencias de participación, votos individuales ni la opción seleccionada por cada usuario.

El endpoint admite únicamente el método `GET`.

Una solicitud con otro método que supera las validaciones generales de seguridad recibe HTTP 405 y el encabezado `Allow: GET`. Una solicitud POST externa sin un token CSRF válido puede ser rechazada previamente con HTTP 403 por la protección CSRF global de Django.

## Autenticación y autorización

- Una cuenta pública puede registrarse, iniciar sesión, consultar el portal y votar.
- Una cuenta pública no puede entrar al panel ni a Django Admin.
- Una cuenta con rol administrativo es dirigida al panel después del inicio de sesión.
- Un superusuario puede acceder al panel y a Django Admin.
- El acceso manual no autorizado a `/administracion/` produce una respuesta HTTP 403 controlada.

Grupos administrativos:

- Administrador general.
- Configurador.
- Operador.
- Publicador.
- Auditor.

## Pruebas automatizadas

### Permisos de MySQL para ejecutar las pruebas

La aplicación utiliza la base principal `festival_votaciones`. Las pruebas automatizadas de Django crean y eliminan una base temporal denominada `test_festival_votaciones`.

El usuario de la aplicación necesita permisos adicionales sobre esa base temporal únicamente cuando se ejecutan las pruebas:

```bash
docker compose \
  --env-file .env.mysql \
  -f compose.mysql.yml \
  exec -T \
  -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" \
  mysql \
  mysql -uroot \
  -e "
GRANT ALL PRIVILEGES
ON \`test_festival_votaciones\`.*
TO '${MYSQL_USER}'@'%';

FLUSH PRIVILEGES;
"
```

Este permiso no convierte al usuario de la aplicación en administrador global de MySQL. Se limita a la base temporal de pruebas.

Puede comprobar los permisos mediante:

```bash
docker compose \
  --env-file .env.mysql \
  -f compose.mysql.yml \
  exec -T \
  -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" \
  mysql \
  mysql -uroot \
  -e "
SHOW GRANTS FOR '${MYSQL_USER}'@'%';
"
```

Comprobaciones generales:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate --plan
```

Suite completa:

```bash
python manage.py test -v 2
```

Resultado de referencia del Eje 3:

```text
114 pruebas ejecutadas
114 pruebas aprobadas
0 fallos
0 errores
Motor: MySQL 8.4
Base temporal: test_festival_votaciones
```

Pruebas específicas:

```bash
python manage.py test elecciones.test_eje3_votacion_categoria -v 2
python manage.py test elecciones.test_eje3_concurrencia -v 2
python manage.py test elecciones.test_eje3_api_categorias -v 2
python manage.py test elecciones.test_preparar_demo_eje3 -v 2
```

Django crea una base temporal y la elimina al finalizar. Los datos de `festival_votaciones` no se alteran.

## Casos de prueba del Eje 3

| Caso | Validación | Resultado esperado |
|---|---|---|
| CP-01 | Voto válido | Se registra una participación y un voto |
| CP-02 | Segundo voto en la misma categoría y edición | Se rechaza y permanece un solo voto |
| CP-03 | Voto en categoría diferente | Se permite |
| CP-04 | Usuario no autenticado | Se redirige al inicio de sesión |
| CP-05 | Categoría no habilitada | Se rechaza la operación |
| CP-06 | Opción perteneciente a otra categoría | Se rechaza sin registrar voto |
| CP-07 | Mis participaciones | Muestra las categorías votadas por el usuario |
| CP-08 | Persistencia administrativa | El registro es consultable en MySQL y administración |
| CP-09 | Dos intentos concurrentes | Solo queda una participación y un voto |
| CP-10 | `GET /api/categorias/` | Devuelve JSON válido con datos reales |

La matriz detallada se conserva en `docs/matriz_casos_prueba_eje3.md`.

## Motores disponibles

- **MySQL:** motor oficial para las evidencias del Eje 3.
- **PostgreSQL:** compatibilidad adicional.
- **SQLite:** alternativa para desarrollo básico.

SQLite no debe utilizarse como evidencia de concurrencia. Las evidencias oficiales deben producirse con MySQL 8.4.

## Seguridad

- Las contraseñas se almacenan mediante hash de Django.
- Las credenciales se leen desde variables externas.
- `.env` y `.env.mysql` no se versionan.
- Los formularios POST utilizan CSRF.
- Las rutas de votación exigen autenticación.
- Las rutas administrativas requieren permisos.
- Django Admin exige una cuenta autorizada.
- El comprobante no revela la opción seleccionada.
- El historial no muestra participaciones de otros usuarios.
- La API no expone información personal ni votos individuales.
- MySQL impide duplicar el voto por usuario, categoría y edición.

## Estructura principal

```text
config/                 Configuración del proyecto Django
elecciones/             Modelos, vistas, formularios, URLs, comandos y pruebas
templates/              Plantillas públicas, administrativas y de autenticación
static/                 CSS, imágenes y recursos públicos
media/                  Imágenes administrables, excluidas de Git
docs/                   Documentación académica y trazabilidad
evidencias/             Capturas y salidas verificables por eje
compose.mysql.yml       Servicio reproducible MySQL 8.4
.env.mysql.example      Plantilla de variables sin secretos
manage.py               Utilidad administrativa de Django
requirements.txt        Dependencias Python
startup.sh              Inicio mediante Gunicorn
```

## Documentación académica

### Eje 2

- `docs/matriz_trazabilidad_eje2.md`
- `docs/pruebas_eje2.md`
- `docs/plan_evidencias_eje2.md`
- `docs/extractos_codigo_eje2.md`
- `evidencias/eje2/`

### Eje 3

- `docs/matriz_casos_prueba_eje3.md`
- `docs/plan_evidencias_eje3.md`
- `docs/extractos_codigo_eje3.md`
- `docs/ficha_acceso_eje3.md`
- `docs/guion_video_eje3.md`
- `evidencias/eje3/`

## Evolución productiva

El repositorio conserva Gunicorn, WhiteNoise y documentación para una posible evolución hacia Azure. La entrega académica no requiere infraestructura de pago.

Una adopción institucional requeriría revisión jurídica y de privacidad, gestión institucional de identidades, protección de secretos, base de datos administrada, almacenamiento persistente de imágenes, pruebas de carga y seguridad, monitoreo, respaldos, recuperación, HTTPS y un servidor WSGI o ASGI.

## Equipo

La actividad es desarrollada por cuatro integrantes. La distribución definitiva de aportes debe registrarse en el PDF conforme al trabajo efectivamente realizado.

## Licencia y finalidad

Prototipo académico. Su uso institucional requiere validación funcional, jurídica, de seguridad, privacidad, capacidad y operación.
