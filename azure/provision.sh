#!/usr/bin/env bash
set -euo pipefail

required=(AZURE_LOCATION AZURE_RESOURCE_GROUP AZURE_PLAN_NAME AZURE_WEBAPP_NAME AZURE_POSTGRES_SERVER AZURE_POSTGRES_DATABASE AZURE_POSTGRES_ADMIN AZURE_POSTGRES_PASSWORD DJANGO_SECRET_KEY)
for var in "${required[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: falta la variable $var" >&2
    exit 1
  fi
done

APP_SERVICE_SKU="${APP_SERVICE_SKU:-B1}"
POSTGRES_SKU="${POSTGRES_SKU:-Standard_B1ms}"
POSTGRES_VERSION="${POSTGRES_VERSION:-15}"
ADMIN_IP="${ADMIN_IP:-$(curl -fsS https://api.ipify.org)}"

echo "Creando grupo de recursos..."
az group create --name "$AZURE_RESOURCE_GROUP" --location "$AZURE_LOCATION" --output none

echo "Creando plan Linux y App Service..."
az appservice plan create \
  --name "$AZURE_PLAN_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --location "$AZURE_LOCATION" \
  --is-linux \
  --sku "$APP_SERVICE_SKU" \
  --output none

az webapp create \
  --name "$AZURE_WEBAPP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --plan "$AZURE_PLAN_NAME" \
  --runtime "PYTHON:3.12" \
  --output none

echo "Creando PostgreSQL Flexible Server con acceso inicial restringido..."
az postgres flexible-server create \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --name "$AZURE_POSTGRES_SERVER" \
  --location "$AZURE_LOCATION" \
  --admin-user "$AZURE_POSTGRES_ADMIN" \
  --admin-password "$AZURE_POSTGRES_PASSWORD" \
  --version "$POSTGRES_VERSION" \
  --sku-name "$POSTGRES_SKU" \
  --storage-size 32 \
  --public-access "$ADMIN_IP" \
  --yes \
  --output none

az postgres flexible-server db create \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --server-name "$AZURE_POSTGRES_SERVER" \
  --database-name "$AZURE_POSTGRES_DATABASE" \
  --output none

echo "Permitiendo exclusivamente las IP de salida del App Service..."
OUTBOUND_IPS="$(az webapp show --resource-group "$AZURE_RESOURCE_GROUP" --name "$AZURE_WEBAPP_NAME" --query possibleOutboundIpAddresses -o tsv)"
IFS=',' read -ra IPS <<< "$OUTBOUND_IPS"
index=1
for ip in "${IPS[@]}"; do
  [[ -z "$ip" ]] && continue
  az postgres flexible-server firewall-rule create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --server-name "$AZURE_POSTGRES_SERVER" \
    --name "appservice-outbound-$index" \
    --start-ip-address "$ip" \
    --end-ip-address "$ip" \
    --output none
  index=$((index + 1))
done

echo "Configurando App Service..."
az webapp config appsettings set \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --name "$AZURE_WEBAPP_NAME" \
  --settings \
    DJANGO_PRODUCTION=True \
    DJANGO_DEBUG=False \
    DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    DJANGO_ALLOWED_HOSTS="$AZURE_WEBAPP_NAME.azurewebsites.net" \
    DJANGO_CSRF_TRUSTED_ORIGINS="https://$AZURE_WEBAPP_NAME.azurewebsites.net" \
    DB_ENGINE=postgresql \
    DB_NAME="$AZURE_POSTGRES_DATABASE" \
    DB_USER="$AZURE_POSTGRES_ADMIN" \
    DB_PASSWORD="$AZURE_POSTGRES_PASSWORD" \
    DB_HOST="$AZURE_POSTGRES_SERVER.postgres.database.azure.com" \
    DB_PORT=5432 \
    DB_SSLMODE=require \
    GUNICORN_WORKERS=2 \
    GUNICORN_TIMEOUT=600 \
    SECURE_HSTS_SECONDS=31536000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  --output none

az webapp config set \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --name "$AZURE_WEBAPP_NAME" \
  --startup-file "startup.sh" \
  --always-on true \
  --http20-enabled true \
  --output none

az webapp log config \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --name "$AZURE_WEBAPP_NAME" \
  --application-logging filesystem \
  --level information \
  --web-server-logging filesystem \
  --output none

echo ""
echo "RECURSOS PREPARADOS"
echo "App: https://$AZURE_WEBAPP_NAME.azurewebsites.net"
echo "PostgreSQL: $AZURE_POSTGRES_SERVER.postgres.database.azure.com"
echo "Base: $AZURE_POSTGRES_DATABASE"
echo "IP administrativa permitida: $ADMIN_IP"
echo ""
echo "Siguiente paso: ejecutar azure/configure-oidc.sh y configurar secretos/variables en GitHub."
