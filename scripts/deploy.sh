#!/bin/bash

# Teams Bot Azure Infrastructure Deployment Script
# This script deploys the Azure resources needed for the Teams bot

set -e

# Configuration
RESOURCE_GROUP_NAME="rg-teamsbot-dev"
LOCATION="eastus"
SUBSCRIPTION_ID=""
DEPLOYMENT_NAME="teamsbot-deployment-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Please log in first."
    az login
fi

# Get subscription ID if not set
if [ -z "$SUBSCRIPTION_ID" ]; then
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    print_info "Using subscription: $SUBSCRIPTION_ID"
fi

# Set the subscription
az account set --subscription "$SUBSCRIPTION_ID"

# Create resource group
print_info "Creating resource group: $RESOURCE_GROUP_NAME"
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"

# Get Microsoft App ID and Password
print_info "Creating Microsoft App Registration for the bot..."

# Create app registration
APP_REGISTRATION=$(az ad app create \
    --display-name "TeamsBot-$(date +%Y%m%d)" \
    --sign-in-audience "AzureADMyOrg" \
    --query "{appId:appId,objectId:id}" \
    -o json)

MICROSOFT_APP_ID=$(echo $APP_REGISTRATION | jq -r '.appId')
APP_OBJECT_ID=$(echo $APP_REGISTRATION | jq -r '.objectId')

print_info "Microsoft App ID: $MICROSOFT_APP_ID"

# Create app secret
print_info "Creating app secret..."
APP_SECRET=$(az ad app credential reset \
    --id "$APP_OBJECT_ID" \
    --append \
    --query password \
    -o tsv)

print_info "App secret created successfully (will be used in deployment)"

# Update parameters file with actual values
print_info "Updating parameters file..."
sed -i.bak \
    -e "s/REPLACE_WITH_YOUR_BOT_APP_ID/$MICROSOFT_APP_ID/g" \
    -e "s/REPLACE_WITH_YOUR_BOT_APP_PASSWORD/$APP_SECRET/g" \
    infrastructure/main.parameters.json

# Deploy the infrastructure
print_info "Deploying Azure infrastructure..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --template-file infrastructure/main.bicep \
    --parameters infrastructure/main.parameters.json \
    --name "$DEPLOYMENT_NAME" \
    --query "properties.outputs" \
    -o json)

# Extract outputs
WEB_APP_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.webAppName.value')
WEB_APP_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.webAppUrl.value')
OPENAI_ENDPOINT=$(echo $DEPLOYMENT_OUTPUT | jq -r '.openAiEndpoint.value')
BOT_SERVICE_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.botServiceName.value')

print_info "Deployment completed successfully!"
print_info "Web App Name: $WEB_APP_NAME"
print_info "Web App URL: $WEB_APP_URL"
print_info "OpenAI Endpoint: $OPENAI_ENDPOINT"
print_info "Bot Service Name: $BOT_SERVICE_NAME"

# Create .env file for local development
print_info "Creating .env file for local development..."
cat > .env << EOF
MicrosoftAppId=$MICROSOFT_APP_ID
MicrosoftAppPassword=$APP_SECRET
MicrosoftAppType=MultiTenant
MicrosoftAppTenantId=$(az account show --query tenantId -o tsv)

AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=GET_FROM_AZURE_PORTAL
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

AZURE_CLIENT_ID=$MICROSOFT_APP_ID
AZURE_CLIENT_SECRET=$APP_SECRET
AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)

PORT=3978
EOF

print_info "Environment file created: .env"

print_warning "IMPORTANT: You need to manually get the Azure OpenAI API key from the Azure portal and update the .env file"
print_info "Navigate to: https://portal.azure.com -> Resource Group: $RESOURCE_GROUP_NAME -> OpenAI Service -> Keys and Endpoint"

print_info "Next steps:"
print_info "1. Update the AZURE_OPENAI_API_KEY in the .env file"
print_info "2. Install Python dependencies: pip install -r requirements.txt"
print_info "3. Run the bot locally: python app.py"
print_info "4. Test the bot in the Bot Framework Emulator or deploy to the Web App"

# Restore original parameters file
mv infrastructure/main.parameters.json.bak infrastructure/main.parameters.json

print_info "Deployment script completed!"