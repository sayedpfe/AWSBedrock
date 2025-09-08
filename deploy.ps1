# One-click deployment script for AWS Bedrock Agent API to Azure
# This script runs all necessary steps in the right order

$ErrorActionPreference = "Stop"

function Show-Intro {
    Clear-Host
    Write-Host "=========================================================" -ForegroundColor Cyan
    Write-Host "    AWS BEDROCK AGENT API - AZURE DEPLOYMENT WIZARD" -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This wizard will deploy your AWS Bedrock Agent API to Azure" -ForegroundColor White
    Write-Host "in just a few simple steps." -ForegroundColor White
    Write-Host ""
    Write-Host "The process includes:" -ForegroundColor Yellow
    Write-Host "  1. Checking and installing required Azure PowerShell modules" -ForegroundColor Yellow
    Write-Host "  2. Logging in to your Azure account" -ForegroundColor Yellow
    Write-Host "  3. Creating the necessary Azure resources" -ForegroundColor Yellow
    Write-Host "  4. Deploying your AWS Bedrock Agent API code" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Prerequisites:" -ForegroundColor Yellow
    Write-Host "  - PowerShell 5.1 or higher" -ForegroundColor Yellow
    Write-Host "  - AWS Bedrock access and credentials" -ForegroundColor Yellow
    Write-Host "  - Azure subscription" -ForegroundColor Yellow
    Write-Host ""
    
    # User prompt - we don't need to store the result
    Read-Host "Press Enter to continue or Ctrl+C to exit"
}

function Test-RequiredFiles {
    $requiredFiles = @(
        "setup_azure_modules.ps1",
        "deploy_wizard.ps1",
        "deploy_to_azure.ps1"
    )
    
    $missingFiles = @()
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Host "ERROR: The following required files are missing:" -ForegroundColor Red
        foreach ($file in $missingFiles) {
            Write-Host "  - $file" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Please make sure all deployment scripts are in the current directory." -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Test-BedrockCode {
    $bedrockFiles = @(
        "simple_agent.py",
        "config.py"
    )
    
    $missingBedrockFiles = @()
    
    foreach ($file in $bedrockFiles) {
        if (-not (Test-Path $file)) {
            $missingBedrockFiles += $file
        }
    }
    
    # Check for at least one API file
    $apiFile = $false
    if (Test-Path "bedrock_api.py") {
        $apiFile = $true
    }
    elseif (Test-Path "app.py") {
        $apiFile = $true
    }
    
    if ($missingBedrockFiles.Count -gt 0 -or -not $apiFile) {
        Write-Host "WARNING: Some AWS Bedrock code files appear to be missing:" -ForegroundColor Yellow
        
        foreach ($file in $missingBedrockFiles) {
            Write-Host "  - $file" -ForegroundColor Yellow
        }
        
        if (-not $apiFile) {
            Write-Host "  - Missing API file (bedrock_api.py or app.py)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "The deployment may fail if required code files are missing." -ForegroundColor Yellow
        
        $continue = Read-Host "Do you want to continue anyway? (y/n)"
        return ($continue -eq "y" -or $continue -eq "Y")
    }
    
    return $true
}

function Get-AwsCredentials {
    $credentialsFile = "aws_credentials.txt"
    
    if (-not (Test-Path $credentialsFile)) {
        Write-Host ""
        Write-Host "AWS credentials file not found." -ForegroundColor Yellow
        Write-Host "You'll be asked for your AWS credentials during deployment," -ForegroundColor Yellow
        Write-Host "or you can create the file now." -ForegroundColor Yellow
        Write-Host ""
        
        $createNow = Read-Host "Do you want to create the AWS credentials file now? (y/n)"
        
        if ($createNow -eq "y" -or $createNow -eq "Y") {
            Write-Host ""
            Write-Host "Enter your AWS credentials:" -ForegroundColor Cyan
            $accessKey = Read-Host "AWS Access Key ID"
            $secretKey = Read-Host "AWS Secret Access Key" -AsSecureString
            $region = Read-Host "AWS Region (e.g., us-west-2)"
            
            # Convert secure string to plain text for file
            $secretKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
                [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretKey)
            )
            
            # Create credentials file
            "aws_access_key_id=$accessKey
aws_secret_access_key=$secretKeyPlain
region=$region" | Set-Content $credentialsFile
            
            Write-Host "AWS credentials file created successfully." -ForegroundColor Green
        }
    }
    else {
        Write-Host "AWS credentials file found." -ForegroundColor Green
    }
}

function Start-SetupCheck {
    Write-Host ""
    Write-Host "Step 1: Checking Azure PowerShell modules..." -ForegroundColor Cyan
    
    & .\setup_azure_modules.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Setup check failed. Please fix the issues before continuing." -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Start-Deployment {
    Write-Host ""
    Write-Host "Step 2: Running deployment wizard..." -ForegroundColor Cyan
    
    & .\deploy_wizard.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Deployment failed. Please check the error messages." -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Show-Completion {
    Write-Host ""
    Write-Host "=========================================================" -ForegroundColor Green
    Write-Host "             DEPLOYMENT PROCESS COMPLETED" -ForegroundColor Green
    Write-Host "=========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your AWS Bedrock Agent API has been deployed to Azure." -ForegroundColor Green
    Write-Host ""
    Write-Host "If you encounter any issues:" -ForegroundColor Yellow
    Write-Host "1. Check the Azure portal for your Web App status" -ForegroundColor Yellow
    Write-Host "2. Review the deployment logs in the Azure portal" -ForegroundColor Yellow
    Write-Host "3. Try accessing the /health endpoint to verify the app is running" -ForegroundColor Yellow
    Write-Host ""
}

# Main script execution
Show-Intro

if (-not (Test-RequiredFiles)) {
    exit 1
}

if (-not (Test-BedrockCode)) {
    exit 1
}

Get-AwsCredentials

if (-not (Start-SetupCheck)) {
    exit 1
}

if (-not (Start-Deployment)) {
    exit 1
}

Show-Completion
