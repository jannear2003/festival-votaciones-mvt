# Sistema de votaciones configurable para el Festival de la Leyenda Vallenata

Aplicación web académica desarrollada con Python, Django y el patrón MVT para administrar ediciones, categorías, votaciones y opciones del Festival de la Leyenda Vallenata.

La versión correspondiente a la actividad evaluativa del Eje 2 utiliza MySQL 8.4 como motor principal. El proyecto conserva compatibilidad adicional con PostgreSQL y SQLite, junto con una ruta documentada para una eventual evolución productiva.

## Alcance académico

La cadena funcional principal es:

```text
Edición -> Categoría -> Votación -> Opción
```

El alcance implementado incluye:

- Ediciones configurables por festival y año.
- Categorías dinámicas vinculadas con una edición.
- Tipos de votación configurables.
- Votaciones con fechas, estados y publicación controlada.
- Opciones o participantes asociados con cada votación.
- Portal público alimentado desde la base de datos.
- Django Admin e interfaces administrativas propias.
- Registro, inicio y cierre de sesión.
- Autorización mediante grupos y permisos de Django.
- Redirección posterior al login según el tipo de cuenta.
- Pruebas automatizadas ejecutadas sobre MySQL.

El registro definitivo de votos, la auditoría avanzada, las pruebas de carga y el despliegue productivo se conservan como capacidades complementarias o evolución futura.

## Arquitectura MVT

- **Modelo:** define festivales, ediciones, categorías, votaciones, opciones y entidades complementarias.
- **Vista:** consulta y procesa información, valida formularios y aplica reglas de navegación.
- **Plantilla:** presenta el portal público, autenticación y administración.

Flujo general:

```text
URL -> Vista -> Modelo/ORM -> Plantilla -> Respuesta HTTP
```

## Tecnologías

- Python 3.12.
- Django 6.0.5.
- MySQL 8.4.
- mysqlclient.
- Docker y Docker Compose.
- HTML y CSS.
- Git y GitHub Codespaces.
- PostgreSQL, Gunicorn y WhiteNoise como capacidades adicionales.

## Requisitos previos

### Ruta recomendada

- GitHub Codespaces, o
- Python 3.12 y Docker con Docker Compose.

### Dependencias Python

Las dependencias se registran en `requirements.txt`.

## Instalación recomendada con MySQL

### 1. Obtener el proyecto

```bash
git clone https://github.com/jannear2003/festival-votaciones-mvt
cd festival-votaciones-mvt
git switch actividad-eje2-mysql
```

### 2. Crear y activar un entorno virtual fuera de Codespaces

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Preparar las variables de MySQL

Copie el archivo de ejemplo:

```bash
cp .env.mysql.example .env.mysql
```

Edite `.env.mysql` y reemplace únicamente las contraseñas ficticias. No confirme este archivo en Git.

### 5. Iniciar MySQL 8.4

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml up -d
```

Compruebe el estado:

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml ps
```

El contenedor `festival-mysql` debe aparecer como `healthy`.

### 6. Configurar Django para MySQL

Cargue las variables del contenedor:

```bash
set -a
source .env.mysql
set +a
```

Exponga las variables que utiliza Django:

```bash
export DB_ENGINE=mysql
export DB_NAME="$MYSQL_DATABASE"
export DB_USER="$MYSQL_USER"
export DB_PASSWORD="$MYSQL_PASSWORD"
export DB_HOST=127.0.0.1
export DB_PORT=3306
```

No muestre ni publique las contraseñas.

### 7. Aplicar migraciones

```bash
python manage.py migrate
```

### 8. Cargar datos de demostración y roles

```bash
python manage.py loaddata datos_desarrollo
python manage.py configurar_roles
```

### 9. Crear un superusuario

```bash
python manage.py createsuperuser
```

La contraseña del superusuario debe ser diferente de las contraseñas de la base de datos.

### 10. Ejecutar la aplicación

```bash
python manage.py runserver 0.0.0.0:8000
```

Rutas principales:

- Portal público: `http://127.0.0.1:8000/`
- Registro: `http://127.0.0.1:8000/cuentas/registro/`
- Inicio de sesión: `http://127.0.0.1:8000/cuentas/login/`
- Panel propio: `http://127.0.0.1:8000/administracion/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## Autenticación y autorización

El sistema diferencia autenticación y autorización:

- Una cuenta pública puede registrarse, iniciar sesión, utilizar el portal y cerrar sesión.
- Una cuenta pública no puede entrar al panel ni a Django Admin.
- Una cuenta con rol administrativo es dirigida al panel después del login.
- Un superusuario puede acceder al panel y a Django Admin.
- El acceso manual no autorizado a `/administracion/` produce una respuesta HTTP 403 controlada.

Grupos administrativos configurados:

- Administrador general.
- Configurador.
- Operador.
- Publicador.
- Auditor.

## Pruebas automatizadas

Ejecute:

```bash
python manage.py check
python manage.py test
```

Resultado de referencia de esta versión:

```text
26 pruebas ejecutadas
26 pruebas aprobadas
0 fallos
0 errores
Motor: MySQL 8.4
Base temporal: test_festival_votaciones
```

Django crea una base temporal para las pruebas y la elimina al terminar, por lo que los datos de demostración de `festival_votaciones` no se alteran.

## Motores disponibles

### MySQL

Motor principal de la actividad evaluativa:

```text
DB_ENGINE=mysql
```

### PostgreSQL

Compatibilidad adicional validada:

```text
DB_ENGINE=postgresql
```

### SQLite

Alternativa local rápida:

```text
DB_ENGINE=sqlite
```

Las evidencias académicas oficiales deben producirse con MySQL.

## Seguridad

- Las contraseñas de usuario se almacenan mediante los mecanismos de hash de Django.
- Las credenciales de las bases se leen desde variables externas.
- `.env` y `.env.mysql` no se versionan.
- Los formularios POST utilizan protección CSRF.
- Las rutas administrativas requieren rol y permisos.
- Django Admin exige una cuenta con `is_staff=True`.

## Estructura principal

```text
config/                 Configuración del proyecto Django
elecciones/             Modelos, vistas, formularios, URLs y pruebas
templates/              Plantillas generales y de autenticación
static/                 CSS, imágenes y recursos públicos
docs/                   Trazabilidad y evidencias técnicas
compose.mysql.yml       Servicio reproducible MySQL 8.4
.env.mysql.example      Plantilla de variables sin secretos
manage.py               Utilidad administrativa de Django
requirements.txt        Dependencias Python
startup.sh              Inicio mediante Gunicorn
```

## Documentación académica

- Matriz de trazabilidad: `docs/matriz_trazabilidad_eje2.md`
- Registro de pruebas: `docs/pruebas_eje2.md`

El PDF final incluirá fragmentos breves de código, explicación técnica, evidencia funcional y relación directa con la rúbrica.

## Códigos relevantes previstos para el PDF

- Configuración de MySQL en `config/settings.py`.
- Relaciones Edición, Categoría, Votación y Opción en `elecciones/models.py`.
- Formulario `RegistroUsuarioForm`.
- Vista `registrar_usuario`.
- Vista `LoginPorRolView`.
- Middleware de autorización.
- Consulta dinámica del portal.
- Pruebas de registro, redirección y acceso administrativo.

## Evolución productiva

El repositorio conserva Gunicorn, WhiteNoise y documentación de Azure. No se aprovisionan recursos de nube para la entrega académica con el fin de evitar costos recurrentes. Una eventual adopción por el Festival requerirá dimensionamiento, pruebas de carga, monitoreo, almacenamiento administrado y controles institucionales.

## Equipo

La actividad requiere cuatro integrantes. La distribución definitiva se registrará en la matriz de trazabilidad y en el PDF conforme al trabajo real de cada integrante.

## Licencia y finalidad

Prototipo académico. Su uso institucional requiere validación funcional, jurídica, de seguridad, privacidad, capacidad y operación.
