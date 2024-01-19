targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Location for the OpenAI resource')
@allowed(['australiaeast', 'canadaeast', 'francecentral', 'swedencentral', 'switzerlandnorth'])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@allowed(['azure', 'openai'])
param openAiHost string // Set in main.parameters.json
@description('Name of the OpenAI resource group. If not specified, the resource group name will be generated.')
param openAiResourceGroupName string = ''

param openAiServiceName string = ''

param openAiSkuName string = 'S0'

param openAiApiKey string = ''
param openAiApiOrganization string = ''

param evalGptDeploymentName string = 'eval'
param evalGptModelName string = 'gpt-4'
param evalGptModelVersion string = '0613'
param evalGptDeploymentCapacity int = 30

@description('Id of the user or app to assign application roles')
param principalId string = ''

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var prefix = '${environmentName}${resourceToken}'
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = if (empty(openAiResourceGroupName)) {
  name: '${prefix}-rg'
  location: location
  tags: tags
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

module openAi 'core/ai/cognitiveservices.bicep' = if (openAiHost == 'azure') {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiServiceName) ? openAiServiceName : '${prefix}-openai'
    location: location
    tags: tags
    sku: {
      name: openAiSkuName
    }
    deployments: [{
      name: evalGptDeploymentName
      model: {
        format: 'OpenAI'
        name: evalGptModelName
        version: evalGptModelVersion
      }
      sku: {
        name: 'Standard'
        capacity: evalGptDeploymentCapacity
      }
    }]
  }
}


// USER ROLES
module openAiRoleUser 'core/security/role.bicep' = if (openAiHost == 'azure') {
  scope: openAiResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'User'
  }
}


output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

// Shared by all OpenAI deployments
output OPENAI_HOST string = openAiHost
output OPENAI_GPT_MODEL string = evalGptModelName
// Specific to Azure OpenAI
output AZURE_OPENAI_SERVICE string = (openAiHost == 'azure') ? openAi.outputs.name : ''
output AZURE_OPENAI_RESOURCE_GROUP string = (openAiHost == 'azure') ? openAiResourceGroup.name : ''
output AZURE_OPENAI_EVAL_DEPLOYMENT string = (openAiHost == 'azure') ? evalGptDeploymentName : ''
// Used only with non-Azure OpenAI deployments
output OPENAI_KEY string = (openAiHost == 'openai') ? openAiApiKey : ''
output OPENAI_ORGANIZATION string = (openAiHost == 'openai') ? openAiApiOrganization : ''
