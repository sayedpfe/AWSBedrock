# Azure Web App Deployment Script for AWS Bedrock Agent API
# This script automates the entire deployment process using Azure PowerShell modules
# No Azure CLI required

param (
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "westus",
    
    [Parameter(Mandatory=$true)]
    [string]$AppName,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$CredentialsPath = "aws_credentials.txt"
)

$ErrorActionPreference = "Stop"

# Function to check if a module is installed
function Test-ModuleInstalled {
    param (
        [string]$ModuleName
    )
    
    if (Get-Module -ListAvailable -Name $ModuleName) {
        Write-Host "Module $ModuleName is installed." -ForegroundColor Green
        return $true
    } 
    else {
        Write-Host "Module $ModuleName is not installed." -ForegroundColor Yellow
        return $false
    }
}

# Function to install a module if not already installed
function Install-ModuleIfNeeded {
    param (
        [string]$ModuleName
    )
    
    if (-not (Test-ModuleInstalled -ModuleName $ModuleName)) {
        Write-Host "Installing module $ModuleName..." -ForegroundColor Cyan
        Install-Module -Name $ModuleName -Scope CurrentUser -Force -AllowClobber
        Write-Host "Module $ModuleName installed successfully." -ForegroundColor Green
    }
}

# Function to read AWS credentials from file
function Get-AwsCredentials {
    param (
        [string]$CredentialsPath
    )
    
    $credentials = @{}
    
    if (Test-Path $CredentialsPath) {
        Get-Content $CredentialsPath | ForEach-Object {
            if ($_ -match "(.+?)=(.+)") {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                $credentials[$key] = $value
            }
        }
    }
    else {
        Write-Error "AWS credentials file not found at: $CredentialsPath"
    }
    
    return $credentials
}

# Function to create deployment package
function New-DeploymentPackage {
    param (
        [string]$SourceDir,
        [string]$ZipPath
    )
    
    # Create a temporary deployment directory
    $deployDir = Join-Path $SourceDir "deploy"
    if (Test-Path $deployDir) {
        Remove-Item -Path $deployDir -Recurse -Force
    }
    New-Item -Path $deployDir -ItemType Directory | Out-Null
    
    # Copy files
    Copy-Item -Path (Join-Path $SourceDir "bedrock_api.py") -Destination (Join-Path $deployDir "app.py")
    Copy-Item -Path (Join-Path $SourceDir "simple_agent.py") -Destination $deployDir
    Copy-Item -Path (Join-Path $SourceDir "config.py") -Destination $deployDir
    
    # Update requirements.txt to include gunicorn
    $requirements = Get-Content -Path (Join-Path $SourceDir "requirements.txt")
    if (-not ($requirements -match "gunicorn")) {
        $requirements += "gunicorn>=20.1.0"
    }
    Set-Content -Path (Join-Path $deployDir "requirements.txt") -Value $requirements
    
    # Create startup command file
    Set-Content -Path (Join-Path $deployDir "startup.sh") -Value "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
    
    # Create the ZIP file
    if (Test-Path $ZipPath) {
        Remove-Item -Path $ZipPath -Force
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($deployDir, $ZipPath)
    
    # Clean up
    Remove-Item -Path $deployDir -Recurse -Force
    
    Write-Host "Deployment package created at: $ZipPath" -ForegroundColor Green
}

# Main script execution starts here
Write-Host "===== AWS Bedrock Agent API - Azure Deployment =====" -ForegroundColor Cyan
Write-Host "This script will deploy your API to Azure App Service" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Check and install required modules
Write-Host "`nChecking for required PowerShell modules..." -ForegroundColor Cyan
Install-ModuleIfNeeded -ModuleName "Az.Accounts"
Install-ModuleIfNeeded -ModuleName "Az.Resources"
Install-ModuleIfNeeded -ModuleName "Az.Websites"

# Check current directory
$currentDir = Get-Location
Write-Host "`nCurrent directory: $currentDir" -ForegroundColor Cyan

# Check if required files exist
$requiredFiles = @("bedrock_api.py", "simple_agent.py", "config.py", "requirements.txt", $CredentialsPath)
$missingFiles = $requiredFiles | Where-Object { -not (Test-Path (Join-Path $currentDir $_)) }

if ($missingFiles.Count -gt 0) {
    Write-Error "Missing required files: $($missingFiles -join ', ')"
    exit 1
}

# Create deployment package
$zipPath = Join-Path $currentDir "deployment.zip"
Write-Host "`nCreating deployment package..." -ForegroundColor Cyan
New-DeploymentPackage -SourceDir $currentDir -ZipPath $zipPath

# Read AWS credentials
Write-Host "`nReading AWS credentials..." -ForegroundColor Cyan
$awsCredentials = Get-AwsCredentials -CredentialsPath $CredentialsPath
if (-not $awsCredentials.ContainsKey("aws_access_key_id") -or 
    -not $awsCredentials.ContainsKey("aws_secret_access_key") -or 
    -not $awsCredentials.ContainsKey("region")) {
    Write-Error "AWS credentials file does not contain required keys (aws_access_key_id, aws_secret_access_key, region)"
    exit 1
}

# Log in to Azure if needed
Write-Host "`nConnecting to Azure..." -ForegroundColor Cyan
try {
    $context = Get-AzContext
    if (-not $context) {
        Connect-AzAccount
    }
    else {
        Write-Host "Already logged in as: $($context.Account)" -ForegroundColor Green
    }
} 
catch {
    Connect-AzAccount
}

# Select subscription if provided
if ($SubscriptionId) {
    Write-Host "`nSelecting subscription: $SubscriptionId" -ForegroundColor Cyan
    Select-AzSubscription -SubscriptionId $SubscriptionId
}

# Create resource group if it doesn't exist
Write-Host "`nChecking resource group: $ResourceGroupName" -ForegroundColor Cyan
$resourceGroup = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue

if (-not $resourceGroup) {
    Write-Host "Creating resource group: $ResourceGroupName in $Location" -ForegroundColor Cyan
    New-AzResourceGroup -Name $ResourceGroupName -Location $Location
}
else {
    Write-Host "Resource group already exists." -ForegroundColor Green
}

# Create App Service Plan
$appServicePlanName = "$AppName-plan"
Write-Host "`nCreating App Service Plan: $appServicePlanName" -ForegroundColor Cyan
$appServicePlan = New-AzAppServicePlan -ResourceGroupName $ResourceGroupName `
                                       -Name $appServicePlanName `
                                       -Location $Location `
                                       -Tier Basic `
                                       -WorkerSize Small `
                                       -Linux

# Create Web App
Write-Host "`nCreating Web App: $AppName" -ForegroundColor Cyan
$webApp = New-AzWebApp -ResourceGroupName $ResourceGroupName `
                       -Name $AppName `
                       -Location $Location `
                       -AppServicePlan $appServicePlanName `
                       -RuntimeStack "PYTHON|3.9"

# Configure app settings
Write-Host "`nConfiguring application settings..." -ForegroundColor Cyan
$appSettings = @{
    "AWS_ACCESS_KEY_ID" = $awsCredentials["aws_access_key_id"];
    "AWS_SECRET_ACCESS_KEY" = $awsCredentials["aws_secret_access_key"];
    "AWS_DEFAULT_REGION" = $awsCredentials["region"];
    "FLASK_APP" = "app.py";
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true";
}

Set-AzWebApp -ResourceGroupName $ResourceGroupName `
             -Name $AppName `
             -AppSettings $appSettings

# Configure general settings with startup command
Write-Host "`nConfiguring startup command..." -ForegroundColor Cyan
$generalSettings = @{
    "linuxFxVersion" = "PYTHON|3.9";
    "appCommandLine" = "gunicorn --bind=0.0.0.0 --timeout 600 app:app";
}

Set-AzWebApp -ResourceGroupName $ResourceGroupName `
             -Name $AppName `
             -AppSettings $appSettings `
             -HttpsOnly $true `
             -AppCommandLine $generalSettings["appCommandLine"]

# Deploy the ZIP package
Write-Host "`nDeploying code package..." -ForegroundColor Cyan
Publish-AzWebApp -ResourceGroupName $ResourceGroupName `
                 -Name $AppName `
                 -ArchivePath $zipPath `
                 -Force

# Get the web app URL
$webAppUrl = "https://$AppName.azurewebsites.net"
Write-Host "`n===== Deployment Complete =====" -ForegroundColor Green
Write-Host "Your API is now deployed to: $webAppUrl" -ForegroundColor Green
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "- Health Check: $webAppUrl/health" -ForegroundColor Cyan
Write-Host "- Simple Agent: $webAppUrl/api/simple-agent" -ForegroundColor Cyan

Write-Host "`nTo test your API, use the following PowerShell command:" -ForegroundColor Cyan
Write-Host "Invoke-RestMethod -Uri '$webAppUrl/health' -Method Get" -ForegroundColor Yellow
Write-Host "Invoke-RestMethod -Uri '$webAppUrl/api/simple-agent' -Method Post -ContentType 'application/json' -Body '{`"input`": `"Hello, how are you?`"}'" -ForegroundColor Yellow

Write-Host "`nOr use the test_api.py script:" -ForegroundColor Cyan
Write-Host "python test_api.py $webAppUrl" -ForegroundColor Yellow
