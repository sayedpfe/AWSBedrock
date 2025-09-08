# Simple wrapper script for deploying the AWS Bedrock Agent API to Azure
# This makes it easy to run the deployment with minimal inputs

# Prompt for required information
Write-Host "===== AWS Bedrock Agent API - Azure Deployment Wizard =====" -ForegroundColor Cyan

# Get resource group name
$resourceGroupName = Read-Host -Prompt "Enter a name for your Azure resource group"
while ([string]::IsNullOrWhiteSpace($resourceGroupName)) {
    Write-Host "Resource group name cannot be empty!" -ForegroundColor Red
    $resourceGroupName = Read-Host -Prompt "Enter a name for your Azure resource group"
}

# Get app name
$appName = Read-Host -Prompt "Enter a globally unique name for your web app (will be used in the URL)"
while ([string]::IsNullOrWhiteSpace($appName)) {
    Write-Host "App name cannot be empty!" -ForegroundColor Red
    $appName = Read-Host -Prompt "Enter a globally unique name for your web app"
}

# Get Azure region with a default
$location = Read-Host -Prompt "Enter Azure region (press Enter for 'westus')"
if ([string]::IsNullOrWhiteSpace($location)) {
    $location = "westus"
}

# Run the deployment script
Write-Host "`nStarting deployment with the following settings:" -ForegroundColor Green
Write-Host "- Resource Group: $resourceGroupName" -ForegroundColor Green
Write-Host "- App Name: $appName" -ForegroundColor Green
Write-Host "- Location: $location" -ForegroundColor Green
Write-Host "`nPress Enter to continue or Ctrl+C to cancel..." -ForegroundColor Yellow
Read-Host

# Execute the main deployment script
$scriptPath = Join-Path (Get-Location) "deploy_to_azure.ps1"
& $scriptPath -ResourceGroupName $resourceGroupName -Location $location -AppName $appName -CredentialsPath "aws_credentials.txt"
