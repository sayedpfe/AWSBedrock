"""
Azure deployment script for AWS Bedrock simple agent API.
This script prepares and deploys the API to Azure App Service.
"""

import os
import subprocess
import sys
import json
import time

def check_azure_cli():
    """Check if Azure CLI is installed."""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Azure CLI not found. Please install it: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
        return True
    except FileNotFoundError:
        print("Azure CLI not found. Please install it: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False

def login_to_azure():
    """Log in to Azure."""
    print("Logging in to Azure...")
    subprocess.run(['az', 'login'], check=True)

def create_resource_group(resource_group, location):
    """Create a resource group if it doesn't exist."""
    print(f"Checking if resource group '{resource_group}' exists...")
    result = subprocess.run(
        ['az', 'group', 'exists', '--name', resource_group],
        capture_output=True, text=True, check=True
    )
    
    if result.stdout.strip() == 'false':
        print(f"Creating resource group '{resource_group}'...")
        subprocess.run(
            ['az', 'group', 'create', '--name', resource_group, '--location', location],
            check=True
        )
    else:
        print(f"Resource group '{resource_group}' already exists.")

def create_app_service_plan(resource_group, plan_name, location):
    """Create an App Service plan."""
    print(f"Creating App Service plan '{plan_name}'...")
    subprocess.run([
        'az', 'appservice', 'plan', 'create',
        '--resource-group', resource_group,
        '--name', plan_name,
        '--sku', 'B1',
        '--location', location
    ], check=True)

def create_web_app(resource_group, app_name, plan_name):
    """Create a Web App."""
    print(f"Creating Web App '{app_name}'...")
    subprocess.run([
        'az', 'webapp', 'create',
        '--resource-group', resource_group,
        '--plan', plan_name,
        '--name', app_name,
        '--runtime', 'PYTHON:3.9'
    ], check=True)

def configure_aws_credentials(resource_group, app_name):
    """Configure AWS credentials as app settings."""
    # Read AWS credentials from file
    aws_credentials = {}
    with open('aws_credentials.txt', 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                aws_credentials[key.strip()] = value.strip()
    
    print("Configuring AWS credentials as app settings...")
    subprocess.run([
        'az', 'webapp', 'config', 'appsettings', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--settings',
        f'AWS_ACCESS_KEY_ID={aws_credentials.get("aws_access_key_id", "")}',
        f'AWS_SECRET_ACCESS_KEY={aws_credentials.get("aws_secret_access_key", "")}',
        f'AWS_DEFAULT_REGION={aws_credentials.get("region", "us-west-2")}'
    ], check=True)

def create_deployment_files():
    """Create required files for Azure deployment."""
    print("Creating deployment configuration files...")
    
    # Create .deployment file
    with open('.deployment', 'w') as f:
        f.write("""[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
""")
    
    # Create startup.txt for Azure
    with open('startup.txt', 'w') as f:
        f.write("gunicorn --bind=0.0.0.0 --timeout 600 bedrock_api:app")

def deploy_to_azure(resource_group, app_name):
    """Deploy the API to Azure App Service."""
    print("Deploying API to Azure App Service...")
    
    # Update requirements.txt to include gunicorn
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    if 'gunicorn' not in content:
        with open('requirements.txt', 'a') as f:
            f.write('\ngunicorn>=20.1.0\n')
    
    # Create a deployment zip file
    import zipfile
    with zipfile.ZipFile('deployment.zip', 'w') as zipf:
        # Add Python files
        for file in os.listdir('.'):
            if file.endswith('.py') or file == 'requirements.txt' or file == '.deployment' or file == 'startup.txt':
                zipf.write(file)
    
    # Deploy the zip file
    subprocess.run([
        'az', 'webapp', 'deployment', 'source', 'config-zip',
        '--resource-group', resource_group,
        '--name', app_name,
        '--src', 'deployment.zip'
    ], check=True)

def main():
    print("=== Deploy AWS Bedrock Agent API to Azure ===")
    
    # Check Azure CLI
    if not check_azure_cli():
        sys.exit(1)
    
    # Login to Azure
    login_to_azure()
    
    # Get user inputs
    resource_group = input("Enter Azure resource group name: ")
    location = input("Enter Azure region (default: westus): ") or "westus"
    app_name_base = input("Enter a base name for your app (will be used for multiple resources): ")
    
    # Create resource names
    plan_name = f"{app_name_base}-plan"
    app_name = f"{app_name_base}-api"
    
    # Create resource group
    create_resource_group(resource_group, location)
    
    # Create App Service plan
    create_app_service_plan(resource_group, plan_name, location)
    
    # Create Web App
    create_web_app(resource_group, app_name, plan_name)
    
    # Configure AWS credentials
    configure_aws_credentials(resource_group, app_name)
    
    # Create deployment files
    create_deployment_files()
    
    # Deploy to Azure
    deploy_to_azure(resource_group, app_name)
    
    print("\n=== Deployment Complete ===")
    print(f"Your API is now deployed to: https://{app_name}.azurewebsites.net/")
    print("\nAPI Endpoints:")
    print(f"- Health Check: https://{app_name}.azurewebsites.net/health")
    print(f"- Simple Agent: https://{app_name}.azurewebsites.net/api/simple-agent")
    
    print("\nTo test your API, use the following curl command:")
    print(f'curl -X POST https://{app_name}.azurewebsites.net/api/simple-agent -H "Content-Type: application/json" -d "{{\\"input\\": \\"Hello, how are you?\\"}}"')

if __name__ == "__main__":
    main()
