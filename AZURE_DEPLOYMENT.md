# AWS Bedrock Agent - Azure Deployment Guide

This repository contains scripts to deploy your AWS Bedrock Agent API to Azure Web App using PowerShell. The deployment is fully automated and doesn't require the Azure CLI.

## Prerequisites

Before you begin, make sure you have:

1. **PowerShell 5.1 or higher** installed on your Windows machine
2. **AWS credentials** with permissions to access Amazon Bedrock
3. **Azure subscription** where you want to deploy the API

## Deployment Files

The repository includes several PowerShell scripts to help with deployment:

- `setup_azure_modules.ps1` - Checks and installs required Azure PowerShell modules
- `deploy_wizard.ps1` - Interactive deployment wizard for easier deployment
- `deploy_to_azure.ps1` - Main deployment script with full configuration options

## Deployment Steps

### Step 1: Check and Install Azure PowerShell Modules

First, run the setup script to check if you have all the required Azure PowerShell modules installed:

```powershell
.\setup_azure_modules.ps1
```

This script will:
- Check your PowerShell version
- Verify if you're running with administrator privileges
- Check execution policy settings
- Check if required Azure modules are installed
- Install missing modules if you confirm
- Verify your Azure login status

### Step 2: Run the Deployment Wizard

For a guided deployment experience, use the deployment wizard:

```powershell
.\deploy_wizard.ps1
```

The wizard will:
- Prompt for Resource Group name
- Prompt for Web App name (must be globally unique)
- Prompt for Azure Region (with default option)
- Display a summary of your choices
- Run the deployment after your confirmation

### Step 3: Advanced Deployment (Optional)

If you need more control over the deployment options, you can run the main deployment script directly:

```powershell
.\deploy_to_azure.ps1 -ResourceGroupName "your-resource-group" -AppName "your-webapp-name" -Location "westus" -AppServicePlanName "your-plan-name" -AppServicePlanTier "B1"
```

Parameters:
- `ResourceGroupName` (Required): Name of the Azure Resource Group
- `AppName` (Required): Name of the Azure Web App (must be globally unique)
- `Location` (Optional, default: "westus"): Azure region
- `AppServicePlanName` (Optional, default: "[AppName]-plan"): Name of the App Service Plan
- `AppServicePlanTier` (Optional, default: "B1"): Tier of the App Service Plan

## Deployment Process

The deployment script performs the following steps:

1. Checks if Azure PowerShell modules are installed
2. Logs in to your Azure account (if not already logged in)
3. Creates a resource group (if it doesn't exist)
4. Creates an App Service Plan (if it doesn't exist)
5. Creates a Linux Web App with Python 3.9 runtime
6. Configures the Web App with your AWS credentials
7. Prepares the deployment package with your code
8. Deploys the package to the Web App

## After Deployment

Once deployment is successful, you'll see a message with URLs for:
- Your API endpoint: `https://your-app-name.azurewebsites.net/api/simple-agent`
- Health check endpoint: `https://your-app-name.azurewebsites.net/health`

## Troubleshooting

If you encounter issues during deployment:

1. **Azure PowerShell modules not installing**: Run PowerShell as Administrator and try again
2. **Deployment fails**: Check the error message and ensure your AWS credentials are correct
3. **Web App not accessible**: Wait a few minutes after deployment as it may take time to start

## AWS Credentials

The script will prompt for your AWS credentials during deployment if they're not found in the `aws_credentials.txt` file. If you want to prepare this file in advance, create it with the following format:

```
aws_access_key_id=YOUR_ACCESS_KEY
aws_secret_access_key=YOUR_SECRET_KEY
region=YOUR_REGION
```

## Security Notes

- The script stores your AWS credentials as Application Settings in your Azure Web App
- These credentials are encrypted at rest in Azure
- Consider using Azure Key Vault for production deployments
- For enhanced security, use Azure Managed Identities and AWS IAM roles where possible

## License

This project is licensed under the MIT License - see the LICENSE file for details.
