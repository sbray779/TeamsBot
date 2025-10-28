# Teams Bot Azure Infrastructure Deployment Script (PowerShell)
# This script deploys the Azure resources needed for the Teams bot

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-teamsbot-dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId = ""
)

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Configuration
$DeploymentName = "teamsbot-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    # Check if Azure CLI is installed
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Write-Error "Azure CLI is not installed. Please install it first."
        exit 1
    }

    # Check if user is logged in
    $accountInfo = az account show 2>$null
    if (-not $accountInfo) {
        Write-Warning "Not logged in to Azure. Please log in first."
        az login
    }

    # Get subscription ID if not set
    if ([string]::IsNullOrEmpty($SubscriptionId)) {
        $SubscriptionId = az account show --query id -o tsv
        Write-Info "Using subscription: $SubscriptionId"
    }

    # Set the subscription
    az account set --subscription $SubscriptionId

    # Create resource group
    Write-Info "Creating resource group: $ResourceGroupName"
    az group create --name $ResourceGroupName --location $Location

    # Get Microsoft App ID and Password
    Write-Info "Creating Microsoft App Registration for the bot..."

    # Create app registration
    $appRegistration = az ad app create `
        --display-name "TeamsBot-$(Get-Date -Format 'yyyyMMdd')" `
        --sign-in-audience "AzureADMyOrg" `
        --query "{appId:appId,objectId:id}" `
        -o json | ConvertFrom-Json

    $microsoftAppId = $appRegistration.appId
    $appObjectId = $appRegistration.objectId

    Write-Info "Microsoft App ID: $microsoftAppId"

    # Create app secret
    Write-Info "Creating app secret..."
    $appSecret = az ad app credential reset `
        --id $appObjectId `
        --append `
        --query password `
        -o tsv

    Write-Info "App secret created successfully"

    # Update parameters file with actual values
    Write-Info "Updating parameters file..."
    $parametersContent = Get-Content "infrastructure\main.parameters.json" -Raw
    $parametersContent = $parametersContent -replace "REPLACE_WITH_YOUR_BOT_APP_ID", $microsoftAppId
    $parametersContent = $parametersContent -replace "REPLACE_WITH_YOUR_BOT_APP_PASSWORD", $appSecret
    $parametersContent | Set-Content "infrastructure\main.parameters.temp.json"

    # Deploy the infrastructure
    Write-Info "Deploying Azure infrastructure..."
    $deploymentOutput = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file "infrastructure\main.bicep" `
        --parameters "infrastructure\main.parameters.temp.json" `
        --name $DeploymentName `
        --query "properties.outputs" `
        -o json | ConvertFrom-Json

    # Extract outputs
    $webAppName = $deploymentOutput.webAppName.value
    $webAppUrl = $deploymentOutput.webAppUrl.value
    $openAiEndpoint = $deploymentOutput.openAiEndpoint.value
    $botServiceName = $deploymentOutput.botServiceName.value

    Write-Info "Deployment completed successfully!"
    Write-Info "Web App Name: $webAppName"
    Write-Info "Web App URL: $webAppUrl"
    Write-Info "OpenAI Endpoint: $openAiEndpoint"
    Write-Info "Bot Service Name: $botServiceName"

    # Get tenant ID
    $tenantId = az account show --query tenantId -o tsv

    # Create .env file for local development
    Write-Info "Creating .env file for local development..."
    $envContent = @"
MicrosoftAppId=$microsoftAppId
MicrosoftAppPassword=$appSecret
MicrosoftAppType=MultiTenant
MicrosoftAppTenantId=$tenantId

AZURE_OPENAI_ENDPOINT=$openAiEndpoint
AZURE_OPENAI_API_KEY=GET_FROM_AZURE_PORTAL
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

AZURE_CLIENT_ID=$microsoftAppId
AZURE_CLIENT_SECRET=$appSecret
AZURE_TENANT_ID=$tenantId

PORT=3978
"@

    $envContent | Set-Content ".env"

    Write-Info "Environment file created: .env"

    Write-Warning "IMPORTANT: You need to manually get the Azure OpenAI API key from the Azure portal and update the .env file"
    Write-Info "Navigate to: https://portal.azure.com -> Resource Group: $ResourceGroupName -> OpenAI Service -> Keys and Endpoint"

    Write-Info "Next steps:"
    Write-Info "1. Update the AZURE_OPENAI_API_KEY in the .env file"
    Write-Info "2. Install Python dependencies: pip install -r requirements.txt"
    Write-Info "3. Run the bot locally: python app.py"
    Write-Info "4. Test the bot in the Bot Framework Emulator or deploy to the Web App"

    Write-Info "Deployment script completed!"

} catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
} finally {
    # Clean up temporary files
    if (Test-Path "infrastructure\main.parameters.temp.json") {
        Remove-Item "infrastructure\main.parameters.temp.json"
    }
}