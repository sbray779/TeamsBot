@description('The name of the Azure OpenAI resource')
param openAiName string = 'openai-${uniqueString(resourceGroup().id)}'

@description('The name of the Bot Service resource')
param botServiceName string = 'botservice-${uniqueString(resourceGroup().id)}'

@description('The name of the App Service Plan')
param appServicePlanName string = 'asp-${uniqueString(resourceGroup().id)}'

@description('The name of the Web App')
param webAppName string = 'webapp-${uniqueString(resourceGroup().id)}'

@description('The location for all resources')
param location string = resourceGroup().location

@description('The SKU for the App Service Plan')
param appServicePlanSku string = 'B1'

@description('The pricing tier for Azure OpenAI')
param openAiSku string = 'S0'

@description('The model deployment name')
param modelDeploymentName string = 'gpt-4'

@description('The model name to deploy')
param modelName string = 'gpt-4'

@description('The model version to deploy')
param modelVersion string = '1106-Preview'

@description('Microsoft App ID for the bot')
param microsoftAppId string

@description('Microsoft App Password for the bot (fallback when Key Vault is not used)')
@secure()
param microsoftAppPassword string = ''

@description('Name of an existing Key Vault that contains the Microsoft App Password secret (optional)')
param keyVaultName string = ''

@description('Name of the secret in Key Vault that stores the Microsoft App Password')
param microsoftAppPasswordSecretName string = 'MicrosoftAppPassword'

// Azure OpenAI Service
resource openAiService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: openAiSku
  }
  properties: {
    customSubDomainName: openAiName
    publicNetworkAccess: 'Enabled'
  }
}

// Model Deployment for Azure OpenAI
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiService
  name: modelDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
    scaleSettings: {
      scaleType: 'Standard'
    }
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: appServicePlanSku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App for hosting the bot
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'MicrosoftAppId'
          value: microsoftAppId
        }
        // If a Key Vault name is provided, point the app setting at the Key Vault secret
        {
          name: 'MicrosoftAppPassword'
          value: (empty(keyVaultName) == false) ? '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=${microsoftAppPasswordSecretName})' : microsoftAppPassword
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAiService.properties.endpoint
        }
        {
          name: 'AZURE_OPENAI_API_KEY'
          value: openAiService.listKeys().key1
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
          value: modelDeploymentName
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
    }
  }
}

// If a Key Vault name was provided, reference the existing Key Vault and grant the web app access
resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' existing = if (empty(keyVaultName) == false) {
  name: keyVaultName
}

resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = if (empty(keyVaultName) == false) {
  // Use a deterministic GUID for the role assignment name. Use webApp.id (known at start) rather than principalId.
  name: guid(keyVault.id, webApp.id, 'kvRole')
  scope: keyVault
  properties: {
    // Key Vault Secrets User role (allows getting secrets)
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: webApp.identity.principalId
  }
}

// Bot Service
resource botService 'Microsoft.BotService/botServices@2022-09-15' = {
  name: botServiceName
  location: 'global'
  sku: {
    name: 'F0'
  }
  kind: 'azurebot'
  properties: {
    displayName: botServiceName
    iconUrl: 'https://docs.botframework.com/static/devportal/client/images/bot-framework-default.png'
    endpoint: 'https://${webApp.properties.defaultHostName}/api/messages'
    msaAppId: microsoftAppId
    // Configure the Bot Service to accept the Web App's managed identity as the bot identity
    // msaAppMSIResourceId expects the resource id of the MSI; for system-assigned identity we can provide the web app resource id
    msaAppMSIResourceId: webApp.id
    msaAppType: 'MSI'
    luisAppIds: []
    schemaTransformationVersion: '1.3'
  isCmekEnabled: false
  }
}

// Teams Channel for the bot
resource teamsChannel 'Microsoft.BotService/botServices/channels@2022-09-15' = {
  parent: botService
  name: 'MsTeamsChannel'
  location: 'global'
  properties: {
    channelName: 'MsTeamsChannel'
    properties: {
      isEnabled: true
    }
  }
}

// Outputs
output webAppName string = webApp.name
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output openAiEndpoint string = openAiService.properties.endpoint
output botServiceName string = botService.name
output resourceGroupName string = resourceGroup().name
