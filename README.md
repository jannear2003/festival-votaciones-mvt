# Sistema de votaciones configurable - Django MVT

Primer incremento práctico del Sistema Web de Votaciones para el Festival de la Leyenda Vallenata.

## Alcance del incremento

- Festival y ediciones configurables.
- Categorías dinámicas por edición.
- Tipos de votación configurables.
- Votaciones y opciones administrables.
- Panel de Django Admin.
- Panel resumen institucional.
- Portal público de consulta.
- Validaciones y pruebas iniciales.

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

- Portal público: http://127.0.0.1:8000/
- Panel resumen: http://127.0.0.1:8000/administracion/
- Django Admin: http://127.0.0.1:8000/admin/

## Pruebas

```bash
python manage.py test
python manage.py check
```

## Regla arquitectónica

Las categorías no son constantes del código. Cada categoría pertenece a una edición y se gestiona desde la base de datos.

## Alternativa sin instalar Python: GitHub Codespaces

1. Cree un repositorio vacío en GitHub.
2. Cargue el contenido de esta carpeta en la raíz del repositorio.
3. Seleccione **Code > Codespaces > Create codespace on main**.
4. Espere a que finalice `postCreateCommand`.
5. En la terminal del Codespace ejecute:

```bash
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

GitHub abrirá una vista previa del puerto 8000. No se necesita instalar Python, Django, Git ni Visual Studio Code en el equipo local.

## Preparación para Azure App Service

El proyecto incluye `gunicorn`, `whitenoise` y `startup.sh`. Para una publicación académica inicial puede desplegarse en Azure App Service Linux. Antes de publicar se deben configurar como variables de aplicación:

```text
DJANGO_SECRET_KEY=<valor-secreto>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<nombre-de-la-app>.azurewebsites.net
```

La base SQLite es únicamente para desarrollo. Antes de una implementación multiusuario se debe configurar PostgreSQL.
