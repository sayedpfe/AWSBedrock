"""
Simple AWS Bedrock Agent - Basic implementation of calling a Bedrock model.

This script demonstrates how to:
1. Set up a connection to AWS Bedrock
2. Format a request for a Bedrock model
3. Process the response from the model

Prerequisites:
- AWS CLI configured with appropriate credentials
- boto3 package installed
- Access to AWS Bedrock service in your AWS account
"""

import json
import boto3
import sys
import os
import time
import traceback
from botocore.exceptions import ClientError, NoCredentialsError, ValidationError
from config import AWS_REGION, MODEL_ID, MAX_TOKENS, TEMPERATURE, TOP_P

class SimpleBedrockAgent:
    def __init__(self):
        """Initialize the Bedrock client."""
        try:
            print(f"Initializing Bedrock client in region {AWS_REGION}")
            
            # Test AWS credentials before creating bedrock client
            self._test_aws_credentials()
                
            # Create the Bedrock runtime client
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=AWS_REGION
            )
            print("Bedrock client initialized successfully")
            
            self.model_id = MODEL_ID
            print(f"Using model: {self.model_id}")
        except NoCredentialsError:
            print("ERROR: No AWS credentials found. Please run 'aws configure'")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR initializing Bedrock client: {str(e)}")
            sys.exit(1)
    
    def _test_aws_credentials(self):
        """Test AWS credentials and print caller identity."""
        try:
            # Get and display AWS credentials info
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                print("❌ No AWS credentials found!")
                print("Run 'aws configure' to set up your credentials")
                return False
                
            # Print masked access key
            access_key = credentials.access_key
            if access_key:
                masked_key = access_key[:4] + "..." + access_key[-4:] if len(access_key) > 8 else "****"
                print(f"✓ Found AWS Access Key: {masked_key}")
            else:
                print("❌ No AWS Access Key found in credentials")
                
            # Get caller identity to verify credentials work
            try:
                sts = boto3.client('sts')
                identity = sts.get_caller_identity()
                
                print(f"✓ AWS Identity verified:")
                print(f"  Account: {identity.get('Account')}")
                print(f"  User ID: {identity.get('UserId')}")
                print(f"  ARN: {identity.get('Arn')}")
                
                return True
            except Exception as e:
                print(f"❌ Failed to verify AWS identity: {str(e)}")
                print("This suggests your credentials may be invalid or expired")
                return False
                
        except Exception as e:
            print(f"❌ Error testing credentials: {str(e)}")
            return False
        
    def _format_prompt_for_model(self, user_input, system_prompt=None):
        """
        Format the prompt based on the model being used.
        Different models require different input formats.
        """
        if "anthropic.claude" in self.model_id:
            # Claude-specific format
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "messages": messages
            }
            
        elif "amazon.titan" in self.model_id:
            # Titan-specific format
            if system_prompt:
                prompt = f"{system_prompt}\n\nHuman: {user_input}\n\nAssistant:"
            else:
                prompt = f"Human: {user_input}\n\nAssistant:"
                
            # Strict format for Titan models
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "topP": TOP_P,
                    "stopSequences": []
                }
            }
            
        elif "meta.llama" in self.model_id:
            # Llama-specific format
            if system_prompt:
                prompt = f"<system>\n{system_prompt}\n</system>\n\n<user>\n{user_input}\n</user>\n\n<assistant>"
            else:
                prompt = f"<user>\n{user_input}\n</user>\n\n<assistant>"
                
            return {
                "prompt": prompt,
                "max_gen_len": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "top_p": TOP_P
            }
            
        elif "mistral" in self.model_id:
            # Mistral-specific format
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            return {
                "messages": messages,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "top_p": TOP_P
            }
            
        else:
            # Generic format (may need adjustment for other models)
            print(f"Using generic format for model: {self.model_id}")
            return {
                "prompt": user_input,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "top_p": TOP_P
            }

    def _extract_response_from_model(self, response_body):
        """
        Extract the generated text from the model response based on the model being used.
        Different models return different response structures.
        """
        if "anthropic.claude" in self.model_id:
            return response_body.get("content", [{}])[0].get("text", "")
            
        elif "amazon.titan" in self.model_id:
            return response_body.get("results", [{}])[0].get("outputText", "")
            
        elif "meta.llama" in self.model_id:
            return response_body.get("generation", "")
            
        else:
            # Generic extraction (may need adjustment for other models)
            return str(response_body)

    def invoke(self, user_input, system_prompt=None):
        """
        Invoke the Bedrock model with the user input.
        
        Args:
            user_input (str): The user's input text/question
            system_prompt (str, optional): System instructions for the model
            
        Returns:
            str: The model's response text
        """
        try:
            # First check if we can list available models to verify access
            try:
                bedrock_client = boto3.client('bedrock', region_name=AWS_REGION)
                print("\nChecking available models in your account...")
                
                response = bedrock_client.list_foundation_models()
                available_models = []
                found_current_model = False
                
                print("\nAvailable models in your account:")
                for model in response.get('modelSummaries', []):
                    model_id = model.get('modelId')
                    access_status = model.get('modelAccessStatus')
                    available_models.append(model_id)
                    
                    if model_id == self.model_id:
                        found_current_model = True
                        print(f"★ {model_id} - Access: {access_status}")
                    else:
                        print(f"  {model_id} - Access: {access_status}")
                
                if not found_current_model:
                    print(f"\nWARNING: Your selected model {self.model_id} is not in your available models list!")
                    print("Consider using one of the available models above instead.")
                    
                    # Suggest a similar model if possible
                    for model_id in available_models:
                        if "titan" in self.model_id.lower() and "titan" in model_id.lower():
                            print(f"Suggestion: Try using {model_id} instead")
                            break
                        elif "claude" in self.model_id.lower() and "claude" in model_id.lower():
                            print(f"Suggestion: Try using {model_id} instead")
                            break
                
            except Exception as list_error:
                print(f"Note: Could not list available models: {str(list_error)}")
                print("This might indicate permission issues with the bedrock:ListFoundationModels action")
            
            # Format the request based on the selected model
            request_body = self._format_prompt_for_model(user_input, system_prompt)
            
            print(f"\nInvoking model: {self.model_id}")
            print(f"Request body format: {json.dumps(request_body, indent=2)}")
            
            # Invoke the model
            print("Calling bedrock-runtime invoke_model API...")
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            print("Got response from model, parsing...")
            response_body = json.loads(response.get("body").read())
            
            # Extract and return the generated text
            result = self._extract_response_from_model(response_body)
            print("Successfully extracted response")
            return result
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", "Unknown error")
            request_id = e.response.get("ResponseMetadata", {}).get("RequestId", "Unknown")
            
            print(f"\nAWS Error ({error_code}): {error_message}")
            print(f"Request ID: {request_id}")
            
            if error_code == "AccessDeniedException":
                print("\n=== Access Denied Troubleshooting ===")
                print("1. MODEL ACCESS: You need to request access to models in AWS Bedrock console")
                print("   Go to: https://console.aws.amazon.com/bedrock/ → Model access → Request model access")
                print("   Enable at least one model (like Amazon Titan Text, Claude, etc.)")
                print("2. IAM PERMISSIONS: Your IAM user needs these permissions:")
                print("   - bedrock:InvokeModel")
                print("   - bedrock:ListFoundationModels")
                print("3. REGION: Ensure you've enabled models in the same region as in config.py")
                print("   Current region: " + AWS_REGION)
                print("4. AWS ACCOUNT: Check if your account has completed verification")
                print("5. SERVICE AVAILABILITY: Verify Bedrock is available in your region")
                print("\nSUGGESTION: Try a different model in config.py, such as:")
                print("   MODEL_ID = 'amazon.titan-text-lite-v1'")
                print("   MODEL_ID = 'anthropic.claude-instant-v1'")
                
            elif error_code == "ValidationException":
                print("\n=== Validation Error Troubleshooting ===")
                print("1. MODEL ID: Check if the model ID is correct and available")
                print("2. REQUEST FORMAT: Ensure your prompt format matches the model requirements")
                print("3. REGION: Verify the model is supported in your selected region")
                print(f"4. ERROR DETAILS: {error_message}")
                
            elif error_code == "ServiceQuotaExceededException":
                print("\n=== Quota Exceeded Troubleshooting ===")
                print("1. USAGE LIMITS: You've hit your usage limits for this model")
                print("2. SOLUTIONS: Wait and try again later or request a quota increase")
                
            elif error_code == "ThrottlingException":
                print("\n=== Throttling Error Troubleshooting ===")
                print("1. TOO MANY REQUESTS: You're sending requests too quickly")
                print("2. SOLUTION: Add delay between requests or implement backoff retry logic")
                
            elif error_code == "ModelNotReadyException":
                print("\n=== Model Not Ready Troubleshooting ===")
                print("1. MODEL UNAVAILABLE: The model is currently unavailable")
                print("2. SOLUTION: Try again later or check AWS status page for outages")
                
            return f"Error ({error_code}): {error_message}"
            
        except Exception as e:
            print(f"\nError invoking Bedrock model: {str(e)}")
            print(f"Error type: {type(e)}")
            
            import traceback
            print("\nDetailed error information:")
            traceback.print_exc()
            
            return f"Error: {str(e)}"


def main():
    """Main function to demonstrate the agent's capabilities."""
    try:
        print("\n============================================")
        print("          AWS BEDROCK SIMPLE AGENT          ")
        print("============================================")
        print(f"Region: {AWS_REGION}")
        print(f"Model: {MODEL_ID}")
        print("Type 'exit' to quit")
        print("============================================")
        
        print("\nStarting agent initialization...")
        
        # Initialize the agent
        agent = SimpleBedrockAgent()
        
        # Test with a simple query first
        print("\n============== RUNNING TEST ===============")
        print("Testing with a simple query...")
        test_response = agent.invoke("Hello, please respond with a brief greeting only.", 
                                    "You are a helpful assistant. Keep responses very short.")
        
        if test_response and not test_response.startswith("Error"):
            print("\n✅ TEST SUCCESSFUL!")
            print("Response: " + test_response)
            print("\nThe agent is working correctly! You can now ask questions.")
        else:
            print("\n❌ TEST FAILED")
            print("Please check the error messages above for troubleshooting.")
            print("If you're having issues with AWS Bedrock access, try:")
            print("1. Using a different model in config.py")
            print("2. Verifying you've enabled model access in the AWS console")
            print("3. Checking your IAM permissions")
            
        print("\n============== INTERACTIVE MODE ==============")
        print("Type your questions below or 'exit' to quit")
        
        # Interactive loop
        while True:
            try:
                user_input = input("\nYour question: ")
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("Goodbye!")
                    break
                
                if not user_input.strip():
                    print("Please enter a question.")
                    continue
                    
                # Add a system prompt (optional)
                system_prompt = "You are a helpful, concise assistant. Provide accurate information."
                
                # Get response from the agent
                response = agent.invoke(user_input, system_prompt)
                
                if response:
                    # Print the response
                    print("\nResponse:")
                    print(response)
                else:
                    print("\nNo response received. Check errors above.")
                    
            except KeyboardInterrupt:
                print("\nOperation interrupted by user.")
                break
            except Exception as e:
                print(f"Error during interaction: {str(e)}")
                
                # Try to recover and continue
                print("Continuing with the next question...")
                continue
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        
        import traceback
        print("\nDetailed error information:")
        traceback.print_exc()
        
        print("\nTroubleshooting suggestions:")
        print("1. Check your AWS credentials with 'aws sts get-caller-identity'")
        print("2. Verify your IAM user has Bedrock permissions")
        print("3. Make sure you've enabled models in the AWS Bedrock console")
        print("4. Try a different region or model in config.py")
        
    finally:
        print("\nThank you for using the AWS Bedrock Simple Agent!")
        

if __name__ == "__main__":
    main()
