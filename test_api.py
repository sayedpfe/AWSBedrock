"""
Test script for the AWS Bedrock agent API.
Run this script to test the API locally before deploying to Azure.
"""

import requests
import json
import sys

def test_local_api():
    """Test the API running locally."""
    print("Testing local API...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/health")
        print("\nHealth Check Response:")
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("Health check failed!")
            return False
    except Exception as e:
        print(f"Error testing health endpoint: {str(e)}")
        print("Make sure the API is running locally (python bedrock_api.py)")
        return False
    
    # Test simple agent endpoint
    try:
        test_input = "Hello, give me a short greeting."
        payload = {
            "input": test_input
        }
        
        print("\nSending request to simple-agent endpoint...")
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post("http://localhost:5000/api/simple-agent", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("Simple agent test failed!")
            return False
            
        print("\nAPI test successful!")
        return True
        
    except Exception as e:
        print(f"Error testing simple agent endpoint: {str(e)}")
        return False

def test_azure_api(azure_url):
    """Test the API deployed to Azure."""
    if not azure_url:
        print("No Azure URL provided. Skipping Azure test.")
        return
    
    print(f"\nTesting Azure API at {azure_url}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{azure_url}/health")
        print("\nHealth Check Response:")
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("Azure health check failed!")
            return False
    except Exception as e:
        print(f"Error testing Azure health endpoint: {str(e)}")
        return False
    
    # Test simple agent endpoint
    try:
        test_input = "Hello, give me a short greeting."
        payload = {
            "input": test_input
        }
        
        print("\nSending request to Azure simple-agent endpoint...")
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{azure_url}/api/simple-agent", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("Azure simple agent test failed!")
            return False
            
        print("\nAzure API test successful!")
        return True
        
    except Exception as e:
        print(f"Error testing Azure simple agent endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== AWS Bedrock Agent API Test ===\n")
    
    if len(sys.argv) > 1:
        # Test Azure API
        azure_url = sys.argv[1]
        test_azure_api(azure_url)
    else:
        # Test local API
        test_local_api()
