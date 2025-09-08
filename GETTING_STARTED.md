# Getting Started with AWS Bedrock Agent

This guide will walk you through the steps to set up and run your AWS Bedrock agent.

## 1. AWS Setup

Before you can run the agent, you need to set up your AWS credentials:

1. **Install AWS CLI** (if not already installed):
   - Windows PowerShell method:
     ```powershell
     # Download the installer
     Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "$env:TEMP\AWSCLIV2.msi"
     
     # Run the installer
     Start-Process -FilePath "$env:TEMP\AWSCLIV2.msi"
     ```
   - Or download from: https://aws.amazon.com/cli/

2. **Configure AWS CLI**:
   ```powershell
   aws configure
   ```
   
   You will be prompted to enter:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (use `us-west-2` for best compatibility with Bedrock)
   - Default output format (json)
   
   ### How to Get Your AWS Credentials:
   
   **Step 1: Create an AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com/
   - Click "Create an AWS Account" and follow the signup process
   - You'll need to provide a credit card, but there's a free tier
   
   **Step 2: Create Access Keys**
   - Sign in to the AWS Management Console
   - Click on your account name in the top-right corner
   - Select "Security credentials"
   - Scroll down to "Access keys" section
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)" as your use case
   - Click through the prompts to create the key
   - IMPORTANT: Save both the Access Key ID and Secret Access Key securely
   - Download the .csv file as a backup

3. **Enable AWS Bedrock and Request Model Access**:
   1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
   2. If you see a "Get started" button, click it
   3. In the left navigation pane, click "Model access"
   4. Click the "Manage model access" button
   5. Check the boxes for the models you want to use:
      - Amazon Titan models (easiest to get started with)
      - Anthropic Claude models (powerful but require approval)
      - Meta Llama models (open source but require approval)
      - Mistral AI models (newer open source models)
   6. Click "Request model access" at the bottom
   7. Wait for approval (Amazon Titan models are typically approved instantly)

## 2. Configuration

1. **Edit `config.py`**:
   - Ensure `AWS_REGION` is set to a region where Bedrock is available (`us-west-2` recommended)
   - Choose a `MODEL_ID` based on the models you have access to:
     ```python
     # Recommended starter models (often approved by default):
     MODEL_ID = "amazon.titan-text-express-v1"  # Balanced performance
     # MODEL_ID = "amazon.titan-text-lite-v1"   # Lighter, faster option
     ```
   - Adjust parameters like `MAX_TOKENS`, `TEMPERATURE`, and `TOP_P` as needed

## 3. Running the Simple Agent

The simple agent provides basic interaction with AWS Bedrock:

```powershell
python simple_agent.py
```

This will start an interactive session where you can ask questions and get responses from the AWS Bedrock model.

## 4. Running the Declarative Agent

The declarative agent provides more structured interaction with AWS Bedrock:

```powershell
python declarative_agent.py
```

This agent can automatically detect different types of requests (questions, summarization, translation, code generation) and handle them appropriately.

## 5. Troubleshooting

### Common Issues and Solutions

#### AccessDeniedException
This means you don't have permission to access the model or service.

**Verify Bedrock Service Access:**
1. Go to AWS Console → Amazon Bedrock
2. Ensure you've completed the initial setup
3. Check if you see a functional dashboard (not a "Get Started" page)

**Verify Model Access:**
1. In the Bedrock console, go to "Model access"
2. Ensure the model you're trying to use is listed and shows "Access granted"
3. If not, click "Manage model access" and request access

**Check IAM Permissions:**
1. In the AWS Console, go to IAM → Users → [Your User]
2. Look at attached policies and ensure they include:
   - `bedrock:InvokeModel`
   - `bedrock:ListFoundationModels`
   - You may need an IAM policy like:
     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Effect": "Allow",
                 "Action": [
                     "bedrock:InvokeModel",
                     "bedrock:ListFoundationModels"
                 ],
                 "Resource": "*"
             }
         ]
     }
     ```

**Try Different Models:**
1. In `config.py`, try changing to a model you definitely have access to:
   ```python
   MODEL_ID = "amazon.titan-text-lite-v1"  # Often available by default
   ```

**Verify Region Compatibility:**
1. Make sure the region in `config.py` is one where Bedrock is available:
   - `us-east-1` (N. Virginia)
   - `us-west-2` (Oregon) - Recommended
   - `eu-central-1` (Frankfurt)
   - `ap-northeast-1` (Tokyo)

#### NoCredentialsError
This means your AWS credentials aren't set up correctly.

**Verify AWS CLI Configuration:**
1. Run `aws configure` again to set up your credentials
2. Check if credentials are working with:
   ```powershell
   aws sts get-caller-identity
   ```
   You should see your AWS account ID, user ID, and ARN

**Check Credential Files:**
1. Look at your AWS credentials file:
   - Windows: `%USERPROFILE%\.aws\credentials`
   - Mac/Linux: `~/.aws/credentials`
2. Ensure it contains your access key and secret key

#### ValidationException
This usually means there's something wrong with your request format.

**Check Model ID:**
1. Verify the model ID in `config.py` is correct
2. List available models with:
   ```powershell
   aws bedrock list-foundation-models --region us-west-2
   ```

**Check Request Format:**
1. The `_format_prompt_for_model` function must match what the model expects
2. Different models require different input formats

### Diagnosing With The Enhanced Agent

The enhanced agent in this project has extensive diagnostics built in:

1. It will check if your AWS credentials are valid
2. It will list available models in your account
3. It will verify if you have access to the selected model
4. It provides detailed error messages with troubleshooting steps

Run the agent and look for these diagnostic messages to pinpoint the issue.

## 6. Understanding AWS Costs

AWS Bedrock is a paid service with the following pricing structure:

- **Pay-per-use**: You're charged based on the number of input and output tokens processed
- **Pricing varies by model**:
  - Amazon Titan Express: ~$0.0003 per 1K input tokens, ~$0.0004 per 1K output tokens
  - Amazon Titan Lite: ~$0.0001 per 1K input tokens, ~$0.0002 per 1K output tokens
  - Claude V2: ~$0.011 per 1K input tokens, ~$0.032 per 1K output tokens
  
**Cost Management Tips:**
- Set up AWS Budgets to monitor your spending
- Use smaller models like Titan Lite for testing
- Implement token limits in your code (already done in the sample code)
- Set `MAX_TOKENS` to a reasonable value in `config.py`

## 7. Next Steps

- Customize the agent behavior in `declarative_agent.py`
- Add new capabilities to handle different types of requests
- Implement a cache to reduce repeated API calls
- Build a web interface or API for your agent
- Add logging and analytics to track usage
