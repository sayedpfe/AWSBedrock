# AWS Bedrock Agent Example

This project demonstrates how to create a simple agent using AWS Bedrock in Python, and then a declarative agent that calls it.

## Prerequisites

1. **AWS Account**: Sign up at https://aws.amazon.com/ if you don't have one
2. **AWS CLI**: Install and configure with your credentials
3. **Python 3.8+**: Required for running the agent code
4. **boto3**: AWS SDK for Python

## Setup Instructions

### 1. AWS CLI Setup

Install the AWS CLI:
- Windows: Download and run the installer from AWS website
- macOS: `brew install awscli`
- Linux: `pip install awscli`

Configure AWS CLI with your credentials:
```powershell
aws configure
```

You'll need to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-west-2)
- Default output format (json)

### 2. Python Environment Setup

Install required packages:
```powershell
pip install boto3 botocore requests
```

### 3. AWS Bedrock Access

**Important**: You must enable access to specific models in AWS Bedrock before using them:

1. Go to the [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access" in the left sidebar
3. Click "Request model access"
4. Select at least one model (Amazon Titan Text models are often available by default)
5. Click "Request model access"

## Project Structure

- `simple_agent.py`: Basic AWS Bedrock agent implementation
- `declarative_agent.py`: Declarative agent that calls the AWS agent
- `config.py`: Configuration settings for the agents
- `requirements.txt`: Python dependencies

## Usage

1. Run the simple agent:
```powershell
python simple_agent.py
```

2. After confirming the simple agent works, run the declarative agent:
```powershell
python declarative_agent.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. AccessDeniedException

If you see an "AccessDeniedException" error:

- **Enable Model Access**: Ensure you've requested access to the model in the AWS Bedrock console
- **IAM Permissions**: Your IAM user needs `bedrock:InvokeModel` and `bedrock:ListFoundationModels` permissions
- **Region Mismatch**: Make sure the region in `config.py` matches where you've enabled the models
- **Try Different Models**: Update `MODEL_ID` in `config.py` to use a model you have access to:
  - `amazon.titan-text-lite-v1` (often available by default)
  - `amazon.titan-text-express-v1` (often available by default)

#### 2. NoCredentialsError

- **AWS CLI Configuration**: Run `aws configure` to set up your credentials
- **Verify Credentials**: Run `aws sts get-caller-identity` to check if your credentials are working

#### 3. ValidationException

- **Model ID**: Double-check the `MODEL_ID` in `config.py` is correct
- **Request Format**: The request format might be incorrect for the chosen model
- **Region Support**: Verify the model is supported in your selected region

### Validating Your Setup

Run these commands to verify your AWS setup:

1. Check your AWS identity:
```powershell
aws sts get-caller-identity
```

2. List available Bedrock models:
```powershell
aws bedrock list-foundation-models --region us-west-2
```

3. Verify model access:
```powershell
aws bedrock get-foundation-model --model-id amazon.titan-text-express-v1 --region us-west-2
```

## Next Steps

- Customize the agent's behavior based on your specific use case
- Add authentication and API endpoints to expose the agent as a service
- Implement caching and error handling for production use
- Try different models and compare their performance
