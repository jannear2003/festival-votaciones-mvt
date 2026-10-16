# Despliegue productivo en Azure

## Arquitectura

- Azure App Service Linux, Python 3.12.
- Azure Database for PostgreSQL Flexible Server 15.
- WhiteNoise para archivos estáticos versionados.
- Gunicorn mediante `startup.sh`.
- GitHub Actions con OIDC.
- Producción como único ambiente permanente.

## 1. Prerrequisitos

Use Azure Cloud Shell Bash o una terminal con Azure CLI. Inicie sesión:

```bash
az login
az account set --subscription "NOMBRE-O-ID-DE-SUSCRIPCION"
```

Confirme disponibilidad de nombres y revise costos en la región antes de crear recursos.

## 2. Definir valores sin guardarlos en Git

```bash
export AZURE_LOCATION="eastus2"
export AZURE_RESOURCE_GROUP="rg-festival-votaciones-prod"
export AZURE_PLAN_NAME="asp-festival-votaciones-prod"
export AZURE_WEBAPP_NAME="festival-votaciones-unico"
export AZURE_POSTGRES_SERVER="pg-festival-votaciones-unico"
export AZURE_POSTGRES_DATABASE="festival_votaciones"
export AZURE_POSTGRES_ADMIN="festivaladmin"
read -s -p "Password PostgreSQL: " AZURE_POSTGRES_PASSWORD; export AZURE_POSTGRES_PASSWORD; echo
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
```

Los nombres de App Service y PostgreSQL deben ser únicos globalmente. Ajuste la región y los nombres antes de ejecutar.

## 3. Crear recursos

```bash
bash azure/provision.sh
```

El script usa por defecto App Service B1 y PostgreSQL `Standard_B1ms`. Revise si estas SKU están disponibles en la suscripción y región. Los recursos generan costos.

## 4. Configurar OIDC

```bash
export GITHUB_OWNER="jannear2003"
export GITHUB_REPO="festival-votaciones-mvt"
bash azure/configure-oidc.sh
```

El script crea una aplicación de Microsoft Entra, su principal de servicio, una credencial federada para el Environment `production` y una asignación Contributor limitada al grupo de recursos. Después puede reducir permisos a roles más específicos.

## 5. Configurar GitHub

En el repositorio, cree el Environment `production`. Agregue estos secretos:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `PROD_DJANGO_SECRET_KEY`
- `PROD_DB_USER`
- `PROD_DB_PASSWORD`

Agregue estas variables de repositorio o del Environment:

- `AZURE_RESOURCE_GROUP`
- `AZURE_WEBAPP_NAME`
- `AZURE_POSTGRES_SERVER`
- `AZURE_POSTGRES_DATABASE`

El valor inicial de `PROD_DB_USER` será el administrador creado para PostgreSQL. Después del primer despliegue se recomienda crear un rol de aplicación con privilegios limitados y sustituir el secreto.

## 6. Primer despliegue

Confirme los archivos y envíelos a `main`. El workflow:

1. crea PostgreSQL temporal;
2. instala dependencias;
3. valida migraciones;
4. ejecuta pruebas;
5. valida `collectstatic`;
6. abre temporalmente el firewall de PostgreSQL para el runner;
7. ejecuta migraciones productivas;
8. elimina la regla temporal incluso si falla el proceso;
9. despliega el ZIP;
10. reinicia y verifica la URL.

```bash
git add .github/workflows/azure-production.yml azure AZURE_DEPLOYMENT.md
git commit -m "Preparar despliegue productivo en Azure"
git push origin main
```

## 7. Datos iniciales y administrador

No se cargan fixtures automáticamente en cada despliegue. Para la primera instalación, abra SSH de App Service o ejecute una consola remota y use:

```bash
python manage.py loaddata datos_desarrollo
python manage.py configurar_roles
python manage.py createsuperuser
```

Ejecute `loaddata` una sola vez. `configurar_roles` es idempotente, pero no necesita ejecutarse en cada despliegue.

## 8. Migraciones

Las migraciones se ejecutan desde GitHub Actions después de superar las pruebas. Deben ser pequeñas, compatibles con la versión desplegada y no destructivas. Producción es el único ambiente permanente, por lo que cambios incompatibles deben dividirse en varias versiones.

## 9. Red y base de datos

El script permite inicialmente:

- la IP administrativa desde la que se aprovisiona;
- las IP de salida conocidas de App Service;
- una IP temporal del runner durante migraciones.

No use la regla `0.0.0.0` como solución permanente. Para una evolución de mayor seguridad, migre a acceso privado con VNet, Private Endpoint, Private DNS y Service Connector.

## 10. Logs y comprobaciones

```bash
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$AZURE_WEBAPP_NAME"
az webapp browse --resource-group "$AZURE_RESOURCE_GROUP" --name "$AZURE_WEBAPP_NAME"
az postgres flexible-server firewall-rule list --resource-group "$AZURE_RESOURCE_GROUP" --name "$AZURE_POSTGRES_SERVER" -o table
```

## 11. Reversión

- El código puede volver a una etiqueta o commit anterior mediante despliegue manual del workflow.
- No revierta migraciones destructivas automáticamente.
- Mantenga migraciones compatibles hacia adelante.
- Antes de cambios de esquema importantes, active respaldo y retención adecuados en PostgreSQL.

## 12. Pendientes posteriores

- Application Insights.
- Alertas de disponibilidad y errores.
- Azure Blob Storage para imágenes cargadas por administración.
- Rol PostgreSQL de mínimo privilegio.
- Acceso privado a PostgreSQL.
- Dominio personalizado y certificado administrado.
