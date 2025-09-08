"""
Simple API for AWS Bedrock agent.
Exposes a single endpoint to interact with the AWS Bedrock simple agent.
"""

import json
import os
from flask import Flask, request, jsonify
from simple_agent import SimpleBedrockAgent
from config import DEFAULT_SYSTEM_PROMPT

app = Flask(__name__)

# Initialize our agent
simple_agent = SimpleBedrockAgent()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint to verify the API is running."""
    return jsonify({
        "status": "healthy",
        "message": "AWS Bedrock agent API is running"
    })

@app.route('/api/simple-agent', methods=['POST'])
def invoke_simple_agent():
    """Endpoint to invoke the simple AWS Bedrock agent directly."""
    data = request.json
    
    if not data or 'input' not in data:
        return jsonify({"error": "Missing required 'input' field"}), 400
    
    user_input = data['input']
    system_prompt = data.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    
    try:
        # Call the simple agent
        response = simple_agent.invoke(user_input, system_prompt)
        return jsonify({
            "response": response,
            "model": simple_agent.model_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
