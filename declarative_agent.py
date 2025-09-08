"""
Declarative AWS Bedrock Agent - A more advanced implementation that uses
a declarative approach to define agent behavior and calls the Simple Bedrock Agent.

This script demonstrates how to:
1. Create a declarative agent with defined behaviors
2. Process user input through structured handling
3. Delegate to the Simple Bedrock Agent for model responses

Prerequisites:
- AWS CLI configured with appropriate credentials
- boto3 package installed
- Access to AWS Bedrock service in your AWS account
- simple_agent.py in the same directory
"""

import json
from simple_agent import SimpleBedrockAgent
from config import DEFAULT_SYSTEM_PROMPT

class DeclarativeAgent:
    """
    A declarative agent that defines its behavior through structured handlers
    and delegates LLM processing to the SimpleBedrockAgent.
    """
    
    def __init__(self):
        """Initialize the declarative agent and its underlying Bedrock agent."""
        # Initialize the simple Bedrock agent
        self.bedrock_agent = SimpleBedrockAgent()
        
        # Define system prompt for the agent
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # Define capabilities and handlers
        self.capabilities = {
            "answer_question": self._handle_general_question,
            "summarize_text": self._handle_summarization,
            "translate_text": self._handle_translation,
            "generate_code": self._handle_code_generation,
            "fallback": self._handle_fallback
        }
        
    def _determine_capability(self, user_input):
        """
        Determine which capability to use based on the user input.
        
        This is a simple rule-based approach. In a more advanced implementation,
        you could use a classifier model or more sophisticated rules.
        
        Args:
            user_input (str): The user's input text
            
        Returns:
            str: The name of the capability to use
        """
        # Convert to lowercase for easier matching
        text = user_input.lower()
        
        # Check for specific patterns in the input
        if any(phrase in text for phrase in ["summarize", "summary", "summarization"]):
            return "summarize_text"
            
        elif any(phrase in text for phrase in ["translate", "translation", "in spanish", "in french"]):
            return "translate_text"
            
        elif any(phrase in text for phrase in ["code", "function", "script", "program", "programming"]):
            return "generate_code"
            
        else:
            # Default to general question answering
            return "answer_question"
    
    def _handle_general_question(self, user_input):
        """Handler for general questions."""
        system_prompt = f"{self.system_prompt}\nAnswer the user's question accurately and concisely."
        return self.bedrock_agent.invoke(user_input, system_prompt)
    
    def _handle_summarization(self, user_input):
        """Handler for summarization requests."""
        # Extract text to summarize (in a real implementation, you'd want better extraction)
        if "summarize" in user_input.lower():
            # Try to extract what comes after "summarize"
            parts = user_input.lower().split("summarize", 1)
            if len(parts) > 1:
                text_to_summarize = parts[1].strip()
            else:
                text_to_summarize = user_input
        else:
            text_to_summarize = user_input
            
        # Create a specific prompt for summarization
        system_prompt = f"{self.system_prompt}\nYou are tasked with summarizing text. Create a concise summary that captures the main points."
        prompt = f"Please summarize the following text:\n\n{text_to_summarize}"
        
        return self.bedrock_agent.invoke(prompt, system_prompt)
    
    def _handle_translation(self, user_input):
        """Handler for translation requests."""
        # This is a simplified implementation
        # In a real system, you'd want to detect source and target languages
        
        system_prompt = f"{self.system_prompt}\nYou are a skilled translator. Translate the text accurately while preserving meaning."
        
        # Try to determine target language (simplified)
        target_language = "Spanish"  # Default
        if "in spanish" in user_input.lower():
            target_language = "Spanish"
        elif "in french" in user_input.lower():
            target_language = "French"
        elif "in german" in user_input.lower():
            target_language = "German"
        # Add more language detection as needed
            
        prompt = f"Translate the following text to {target_language}:\n\n{user_input}"
        
        return self.bedrock_agent.invoke(prompt, system_prompt)
    
    def _handle_code_generation(self, user_input):
        """Handler for code generation requests."""
        system_prompt = f"{self.system_prompt}\nYou are an expert programmer. Generate clean, efficient, and well-commented code based on the requirements."
        
        prompt = f"Generate code for the following requirement:\n\n{user_input}\n\nPlease include comments and explain any non-obvious parts."
        
        return self.bedrock_agent.invoke(prompt, system_prompt)
    
    def _handle_fallback(self, user_input):
        """Fallback handler for when no specific capability matches."""
        system_prompt = f"{self.system_prompt}\nRespond helpfully to the user's input."
        return self.bedrock_agent.invoke(user_input, system_prompt)
    
    def process(self, user_input):
        """
        Process the user input through the declarative agent.
        
        Args:
            user_input (str): The user's input text
            
        Returns:
            str: The agent's response
        """
        try:
            # Determine which capability to use
            capability_name = self._determine_capability(user_input)
            
            # Get the corresponding handler
            handler = self.capabilities.get(capability_name, self.capabilities["fallback"])
            
            # Process the input with the selected handler
            response = handler(user_input)
            
            return response
            
        except Exception as e:
            print(f"Error in declarative agent: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"


def main():
    """Main function to demonstrate the declarative agent's capabilities."""
    agent = DeclarativeAgent()
    
    print("AWS Bedrock Declarative Agent")
    print("This agent uses a declarative approach to process your requests")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        user_input = input("\nYour input: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
            
        # Process the input through the declarative agent
        response = agent.process(user_input)
        
        # Print the response
        print("\nResponse:")
        print(response)


if __name__ == "__main__":
    main()
