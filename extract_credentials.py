"""
Script to extract AWS credentials from aws_credentials.txt file.
"""

def read_aws_credentials():
    """Read AWS credentials from file."""
    credentials = {}
    
    try:
        with open('aws_credentials.txt', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    credentials[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading AWS credentials: {str(e)}")
    
    return credentials

if __name__ == "__main__":
    credentials = read_aws_credentials()
    
    print("AWS Credentials:")
    print(f"AWS_ACCESS_KEY_ID: {credentials.get('aws_access_key_id', '')}")
    print(f"AWS_SECRET_ACCESS_KEY: {credentials.get('aws_secret_access_key', '')} (masked for security)")
    print(f"AWS_DEFAULT_REGION: {credentials.get('region', '')}")
