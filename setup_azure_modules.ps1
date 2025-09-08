# Script to verify Azure PowerShell modules are installed
# and install them if they're missing

$ErrorActionPreference = "Stop"

Write-Host "===== Azure PowerShell Module Setup =====" -ForegroundColor Cyan

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

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell Version: $psVersion" -ForegroundColor Cyan

if ($psVersion.Major -lt 5) {
    Write-Host "WARNING: PowerShell 5.0 or higher is recommended for Azure PowerShell modules." -ForegroundColor Yellow
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host "Running as Administrator: $isAdmin" -ForegroundColor $(if ($isAdmin) { "Green" } else { "Yellow" })

if (-not $isAdmin) {
    Write-Host "Some module installations may require administrator privileges." -ForegroundColor Yellow
    Write-Host "If installation fails, try running this script as Administrator." -ForegroundColor Yellow
}

# Check execution policy
$executionPolicy = Get-ExecutionPolicy
Write-Host "Current Execution Policy: $executionPolicy" -ForegroundColor Cyan

if ($executionPolicy -eq "Restricted") {
    Write-Host "WARNING: Restricted execution policy may prevent module installation." -ForegroundColor Red
    Write-Host "Consider changing the execution policy with:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned" -ForegroundColor Yellow
}

# Check required modules
$requiredModules = @("Az.Accounts", "Az.Resources", "Az.Websites")
$missingModules = @()

foreach ($module in $requiredModules) {
    if (-not (Test-ModuleInstalled -ModuleName $module)) {
        $missingModules += $module
    }
}

# Install missing modules
if ($missingModules.Count -gt 0) {
    Write-Host "`nThe following modules need to be installed: $($missingModules -join ', ')" -ForegroundColor Yellow
    
    $installNuGet = $false
    if (-not (Get-PackageProvider -Name NuGet -ErrorAction SilentlyContinue)) {
        $installNuGet = $true
        Write-Host "NuGet package provider is required and will be installed." -ForegroundColor Yellow
    }
    
    $continue = Read-Host -Prompt "Do you want to install these modules now? (Y/N)"
    
    if ($continue -eq "Y" -or $continue -eq "y") {
        # Install NuGet if needed
        if ($installNuGet) {
            Write-Host "Installing NuGet package provider..." -ForegroundColor Cyan
            Install-PackageProvider -Name NuGet -Force -Scope CurrentUser
        }
        
        # Set PSGallery as trusted
        Write-Host "Setting PSGallery as a trusted repository..." -ForegroundColor Cyan
        if (-not (Get-PSRepository -Name PSGallery -ErrorAction SilentlyContinue).InstallationPolicy -eq "Trusted") {
            Set-PSRepository -Name PSGallery -InstallationPolicy Trusted
        }
        
        # Install Az modules
        foreach ($module in $missingModules) {
            Write-Host "Installing module $module..." -ForegroundColor Cyan
            try {
                Install-Module -Name $module -Scope CurrentUser -Force -AllowClobber
                Write-Host "Module $module installed successfully." -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to install module $module. Error: $_" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "Module installation skipped. Deployment script may fail without these modules." -ForegroundColor Yellow
    }
}
else {
    Write-Host "`nAll required Azure PowerShell modules are installed!" -ForegroundColor Green
}

# Check if user is logged in to Azure
Write-Host "`nChecking Azure login status..." -ForegroundColor Cyan
try {
    $context = Get-AzContext -ErrorAction SilentlyContinue
    if ($context) {
        Write-Host "You are currently logged in to Azure as: $($context.Account)" -ForegroundColor Green
        Write-Host "Current subscription: $($context.Subscription.Name) ($($context.Subscription.Id))" -ForegroundColor Green
    }
    else {
        Write-Host "You are not currently logged in to Azure." -ForegroundColor Yellow
        Write-Host "The deployment script will prompt you to log in." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Unable to check Azure login status. You may not be logged in." -ForegroundColor Yellow
    Write-Host "The deployment script will prompt you to log in." -ForegroundColor Yellow
}

Write-Host "`n===== Setup Complete =====" -ForegroundColor Green
Write-Host "You can now run the deployment wizard with:" -ForegroundColor Cyan
Write-Host ".\deploy_wizard.ps1" -ForegroundColor Yellow
