#!/usr/bin/env bash
set -euo pipefail

required=(AZURE_RESOURCE_GROUP AZURE_WEBAPP_NAME GITHUB_OWNER GITHUB_REPO)
for var in "${required[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: falta la variable $var" >&2
    exit 1
  fi
done

SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
TENANT_ID="$(az account show --query tenantId -o tsv)"
APP_DISPLAY_NAME="${OIDC_APP_NAME:-festival-votaciones-github}"

APP_ID="$(az ad app create --display-name "$APP_DISPLAY_NAME" --query appId -o tsv)"
APP_OBJECT_ID="$(az ad app show --id "$APP_ID" --query id -o tsv)"
SP_OBJECT_ID="$(az ad sp create --id "$APP_ID" --query id -o tsv)"

SCOPE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP"
az role assignment create \
  --role Contributor \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --scope "$SCOPE" \
  --output none

cat > /tmp/federated-credential.json <<EOF
{
  "name": "github-main-production",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:${GITHUB_OWNER}/${GITHUB_REPO}:environment:production",
  "description": "Despliegue de main al ambiente production",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

az ad app federated-credential create \
  --id "$APP_OBJECT_ID" \
  --parameters /tmp/federated-credential.json \
  --output none
rm /tmp/federated-credential.json

echo "Configure estos secretos de GitHub Actions:"
echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
echo ""
echo "Cree tambien PROD_DJANGO_SECRET_KEY, PROD_DB_USER y PROD_DB_PASSWORD."
echo "Use un Environment de GitHub llamado production con aprobacion manual si su plan lo permite."
