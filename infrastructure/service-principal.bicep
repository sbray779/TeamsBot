@description('The name of the service principal')
param servicePrincipalName string = 'sp-teamsbot-${uniqueString(resourceGroup().id)}'

@description('The description of the service principal')
param servicePrincipalDescription string = 'Service Principal for Teams Bot Azure OpenAI Access'

@description('The resource group where resources will be deployed')
param targetResourceGroupName string = resourceGroup().name

@description('The subscription ID where resources will be deployed')
param targetSubscriptionId string = subscription().subscriptionId

// Service Principal (Application Registration)
resource servicePrincipal 'Microsoft.Graph/applications@2021-06-01' = {
  displayName: servicePrincipalName
  description: servicePrincipalDescription
  signInAudience: 'AzureADMyOrg'
  api: {
    requestedAccessTokenVersion: 2
  }
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000' // Microsoft Graph
      resourceAccess: [
        {
          id: 'e1fe6dd8-ba31-4d61-89e7-88639da4683d' // User.Read
          type: 'Scope'
        }
      ]
    }
  ]
}

// Service Principal Secret
resource servicePrincipalSecret 'Microsoft.Graph/applications/passwords@2021-06-01' = {
  parent: servicePrincipal
  displayName: 'TeamsBot Secret'
  endDateTime: dateTimeAdd(utcNow(), 'P2Y') // Valid for 2 years
}

// Role Assignment for Cognitive Services
resource cognitiveServicesRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: resourceGroup()
  name: guid(servicePrincipal.id, 'CognitiveServicesUser', resourceGroup().id)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908') // Cognitive Services User
    principalId: servicePrincipal.id
    principalType: 'ServicePrincipal'
  }
}

// Role Assignment for App Service
resource webAppRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: resourceGroup()
  name: guid(servicePrincipal.id, 'WebsiteContributor', resourceGroup().id)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'de139f84-1756-47ae-9be6-808fbbe84772') // Website Contributor
    principalId: servicePrincipal.id
    principalType: 'ServicePrincipal'
  }
}

// Output the service principal details
output servicePrincipalId string = servicePrincipal.id
output servicePrincipalAppId string = servicePrincipal.appId
output servicePrincipalSecret string = servicePrincipalSecret.secretText
output servicePrincipalDisplayName string = servicePrincipal.displayName