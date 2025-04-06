import os
import sys
import logging
import anthropic
from anthropic import Anthropic
from flask import current_app

logger = logging.getLogger(__name__)

class AnthropicAI:
    """Integration with Anthropic's Claude models for AI chat functionality"""
    
    def __init__(self):
        # Initialize the Anthropic client
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            logger.error("ANTHROPIC_API_KEY environment variable is not set")
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        
        self.client = Anthropic(
            api_key=self.anthropic_key,
        )
        
        # The newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        self.model = "claude-3-5-sonnet-20241022" 
        
        # System prompt for the recruiting assistant
        self.system_prompt = """
        You are Helix, an agentic recruiting assistant designed to help with outreach and engagement for hiring candidates.
        
        Your main functions are:
        1. Helping users create personalized outreach sequences for different recruiting roles and scenarios
        2. Providing insights and suggestions for recruiting strategies
        3. Assisting with writing recruiting messages, emails, and other communications
        
        When helping with sequences:
        - Ask for clarifying details about the role, desired qualifications, and company culture
        - Tailor messages to be engaging, professional, and personalized
        - Consider the appropriate tone and style for the industry and seniority level
        - Suggest multiple follow-up steps and templates for a complete outreach sequence
        
        Guidelines:
        - Be helpful, friendly, and professional
        - Avoid generic, overly formal language
        - Include specific details when provided
        - Suggest improvements to user-provided content when appropriate
        - Focus on creating authentic, personalized communication that respects candidates' time and experience
        """
        
    def get_chat_response(self, user_message, chat_history=None):
        """
        Get a response from Claude based on the user message and chat history
        
        Args:
            user_message (str): The most recent user message
            chat_history (list, optional): List of previous messages as dicts with 'role' and 'content'
        
        Returns:
            str: The assistant's response text
        """
        try:
            # Format the messages for the Anthropic API
            messages = []
            
            # Add chat history if provided
            if chat_history:
                for message in chat_history:
                    # Skip system messages as they should be in the system parameter
                    if message["role"] == "system":
                        continue
                    messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call the Anthropic API
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                system=self.system_prompt,  # Use system parameter instead of a system message
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract and return the assistant's response
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            return f"I apologize, but I encountered an error processing your request. Please try again. (Error: {str(e)})"
    
    def generate_outreach_sequence(self, job_title, company_name, details=None):
        """
        Generate a complete outreach sequence for a recruiting scenario
        
        Args:
            job_title (str): The job title for the role
            company_name (str): The company name
            details (str, optional): Additional details about the role and requirements
        
        Returns:
            list: A list of sequence steps with type and content
        """
        try:
            prompt = f"""
            Create a recruiting outreach sequence for a {job_title} role at {company_name}.
            
            Additional details:
            {details if details else 'No additional details provided.'}
            
            Please provide a complete sequence with:
            1. Initial outreach email
            2. Follow-up message
            3. Final connection attempt
            
            For each step, include the appropriate type (email, message, call) and content.
            Format the response as a valid JSON array with 'type' and 'content' fields for each step.
            Format your ENTIRE response as valid JSON:

            ```json
            [
                {{
                    "type": "email",
                    "content": "Subject: Opportunity at Company\\n\\nHi {{name}},\\n\\n[Email content]"
                }},
                {{
                    "type": "message",
                    "content": "Follow-up content here"
                }},
                {{
                    "type": "call",
                    "content": "Final call script here"
                }}
            ]
            ```

            Do not include any explanations or text outside of the JSON structure. The entire response must be valid JSON that can be parsed with json.loads().
            """
            
            # Call the Anthropic API
            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system=self.system_prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract and parse the JSON response
            import json
            import re
            
            # Extract JSON content
            assistant_response = response.content[0].text
            
            # Try to extract JSON array
            json_str = assistant_response
            
            # Look for JSON code blocks
            match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', assistant_response)
            if match:
                json_str = match.group(1)
            else:
                # Try to find array directly
                match = re.search(r'(\[[\s\S]*?\])', assistant_response)
                if match:
                    json_str = match.group(1)
                    
            logger.debug(f"Extracted JSON string: {json_str}")
            
            # Clean up the string - remove any comments
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            
            # Parse JSON
            sequence_steps = json.loads(json_str)
            return sequence_steps
            
        except Exception as e:
            logger.error(f"Error generating outreach sequence: {str(e)}")
            return None

# Create a singleton instance
ai_service = AnthropicAI()