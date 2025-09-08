# AWS Bedrock Agent API on Azure

This guide explains how to run the AWS Bedrock agent API locally and deploy it to Azure.

## Local Setup

### Prerequisites

1. Python 3.8+ installed
2. AWS credentials configured
3. Flask installed (`pip install flask`)

### Running Locally

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Start the API server:
   ```
   python bedrock_api.py
   ```

3. Test the API using the test script:
   ```
   python test_api.py
   ```

4. Or test using curl:
   ```
   curl -X GET http://localhost:5000/health
   
   curl -X POST http://localhost:5000/api/simple-agent \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello, how are you?"}'
   ```

## Azure Deployment

### Prerequisites

1. Azure account
2. Azure CLI installed
3. Subscription with permissions to create resources

### Deployment Steps

1. Run the deployment script:
   ```
   python azure_deploy.py
   ```

2. Follow the prompts to provide:
   - Resource group name
   - Azure region
   - Base name for your app

3. The script will:
   - Create a resource group (if it doesn't exist)
   - Create an App Service plan
   - Create a Web App
   - Configure AWS credentials as environment variables
   - Deploy your API code

4. After deployment, test your API using the test script:
   ```
   python test_api.py https://your-app-name.azurewebsites.net
   ```

### Azure Resource Management

- **Viewing logs**: 
  ```
  az webapp log tail --name your-app-name --resource-group your-resource-group
  ```

- **Restarting the app**:
  ```
  az webapp restart --name your-app-name --resource-group your-resource-group
  ```

- **Scaling up/down**:
  ```
  az appservice plan update --name your-plan-name --resource-group your-resource-group --sku S1
  ```

## API Usage

### Endpoints

- **Health Check**: `GET /health`
  - Returns the status of the API
  - Example response:
    ```json
    {
      "status": "healthy",
      "message": "AWS Bedrock agent API is running"
    }
    ```

- **Simple Agent**: `POST /api/simple-agent`
  - Invokes the AWS Bedrock simple agent
  - Request body:
    ```json
    {
      "input": "Your question or prompt here",
      "system_prompt": "Optional system prompt here"
    }
    ```
  - Example response:
    ```json
    {
      "response": "The agent's response text",
      "model": "amazon.titan-text-lite-v1"
    }
    ```

### Common Errors

- **400 Bad Request**: Missing required 'input' field
- **500 Internal Server Error**: Error invoking the AWS Bedrock agent

## Security Considerations

- AWS credentials are stored as application settings in Azure App Service
- By default, the API has no authentication - add authentication for production use
- Consider using Azure Key Vault for storing sensitive information

## Monitoring

- Enable Application Insights for detailed monitoring
- Set up alerts for errors and performance issues
- Monitor usage to control costs

## Adding Azure Entra ID Authentication (Future Enhancement)

To add Azure Entra ID authentication:

1. Register an application in Azure Entra ID
2. Create an App Registration in the Azure portal
3. Configure the web app with authentication settings
4. Update the API code to validate tokens

## Troubleshooting

- **API not responding**: Check the App Service logs
- **Deployment failures**: Verify Python version compatibility
- **AWS errors**: Ensure AWS credentials are correctly configured
- **Module not found errors**: Check if all requirements are in requirements.txt
