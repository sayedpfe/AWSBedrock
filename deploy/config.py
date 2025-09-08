"""
Configurat# RECOMMENDED STARTER MODELS - These are often available by default:
# MODEL_ID = "amazon.titan-text-express-v1"  # Amazon Titan Express - Good balance of quality and speed

# ALTERNATIVE MODELS TO TRY - Uncomment one of these if the above doesn't work:
MODEL_ID = "amazon.titan-text-lite-v1"     # Amazon Titan Lite - Faster, less powerfulettings for AWS Bedrock agents.
Update these values based on your AWS setup and preferences.
"""

# AWS Configuration
AWS_REGION = "us-west-2"  # Region where you've enabled Bedrock models
# Common regions with Bedrock support: us-east-1, us-west-2, eu-central-1, ap-northeast-1

# ===========================
# BEDROCK MODEL CONFIGURATION
# ===========================
# IMPORTANT: You must request access to models in the AWS Bedrock console before using them
# Go to: https://console.aws.amazon.com/bedrock/ → Model access → Request model access

# RECOMMENDED STARTER MODELS - These are often available by default:
MODEL_ID = "amazon.titan-text-lite-v1"  # Amazon Titan Express - Good balance of quality and speed

# ALTERNATIVE MODELS TO TRY - Uncomment one of these if the above doesn't work:
# MODEL_ID = "amazon.titan-text-lite-v1"     # Amazon Titan Lite - Faster, less powerful
# MODEL_ID = "anthropic.claude-instant-v1"   # Claude Instant - Fast responses (requires approval)
# MODEL_ID = "anthropic.claude-v2"           # Claude V2 - High quality (requires approval)
# MODEL_ID = "meta.llama2-13b-chat-v1"       # Llama 2 - Open source model (requires approval)
# MODEL_ID = "mistral.mistral-7b-instruct-v0:2" # Mistral - Efficient open model (requires approval)

# ============================
# MODEL RESPONSE CONFIGURATION
# ============================
MAX_TOKENS = 1024  # Maximum tokens in response (higher = longer responses)
                   # Typical ranges: 256 (short) to 4096 (very long)

TEMPERATURE = 0.7  # Randomness (0.0-1.0)
                   # Lower (0.1-0.4): More factual, consistent
                   # Higher (0.7-1.0): More creative, varied

TOP_P = 0.9  # Controls diversity of responses (0.0-1.0)
             # Lower (0.5): More focused responses
             # Higher (0.9-1.0): More diverse responses

# ============================
# AGENT BEHAVIOR CONFIGURATION
# ============================
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant that answers user questions accurately and concisely."""

# Alternative system prompts (replace the above with one of these for different behavior):
# ANALYTICAL_PROMPT = """You are an analytical assistant that provides detailed, evidence-based analysis."""
# CREATIVE_PROMPT = """You are a creative assistant that generates imaginative ideas and content."""
# TECHNICAL_PROMPT = """You are a technical assistant that explains complex concepts clearly."""
