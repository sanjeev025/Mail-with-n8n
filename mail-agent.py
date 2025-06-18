import os
import requests
from dotenv import load_dotenv
import logging
from typing import Dict, Optional,Tuple,List
import json
import re
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class N8nEmailSender:
    def __init__(self):
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL')
        self.api_key = os.getenv('N8N_API_KEY')
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.n8n_webhook_url or not self.api_key:
            raise ValueError("N8N_WEBHOOK_URL and N8N_API_KEY must be set in environment variables")
        
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY must be set in environment variables")
            
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_llm_content(self, prompt: str) -> Optional[str]:
        """
        Generate content using Google's Gemini LLM
        
        Args:
            prompt: The prompt to generate content from
            
        Returns:
            Optional[str]: Generated content or None if generation fails
        """
        try:
            # Create a more detailed prompt for email content
            enhanced_prompt = f"""
            Please generate professional email content based on the following request:
            {prompt}
            
            Requirements:
            - Keep the tone professional and engaging
            - Structure the content with clear paragraphs
            - Include relevant details and context
            - End with a clear call to action or conclusion
            """
            
            # Generate content using Gemini
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                return response.text
            else:
                logger.error("Empty response from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error generating LLM content: {str(e)}")
            return None

    def send_email(self, 
                  recipient: str, 
                  subject: str, 
                  prompt: str,
                  template_id: Optional[str] = None) -> bool:
        """
        Send an email using n8n webhook
        
        Args:
            recipient: Email address of the recipient
            subject: Email subject
            prompt: Prompt for LLM content generation
            template_id: Optional template ID for email formatting
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Generate content using LLM
            content = self.generate_llm_content(prompt)
            if not content:
                return False

            # Prepare payload for n8n webhook
            payload = {
                "recipient": recipient,
                "subject": subject,
                "content": content,
                "template_id": template_id
            }

            # Send request to n8n webhook
            headers = {
                "Content-Type": "application/json",
                "X-N8N-API-KEY": self.api_key
            }

            logger.info(f"Attempting to send request to n8n webhook: {self.n8n_webhook_url}")
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                logger.info(f"Email sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                logger.error(f"Request URL: {self.n8n_webhook_url}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailAgent:
    def __init__(self):
        """Initialize the EmailAgent with N8nEmailSender instance."""
        self.email_sender = N8nEmailSender()
        
    def process_user_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Process the user's prompt and generate appropriate email content.
        
        Args:
            prompt: User's input prompt for email generation
            
        Returns:
            Tuple[bool, str]: (Success status, Response message)
        """
        try:
            # Extract email details from the prompt
            email_details = self._parse_prompt(prompt)
            if not email_details:
                return False, "Could not extract email details from the prompt"
            
            # Send the email
            success = self.email_sender.send_email(
                recipient=email_details['recipient'],
                subject=email_details['subject'],
                prompt=email_details['content_prompt'],
                template_id=email_details.get('template_id')
            )
            
            if success:
                return True, f"Email sent successfully to {email_details['recipient']}"
            else:
                return False, "Failed to send email"
                
        except Exception as e:
            logger.error(f"Error processing user prompt: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _parse_prompt(self, prompt: str) -> Optional[Dict]:
        """
        Parse the user's prompt to extract email details.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Optional[Dict]: Dictionary containing email details or None if parsing fails
        """
        try:
            # First, try to extract email and subject using regex
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            subject_pattern = r'subject:([^,]+)'
            
            email_match = re.search(email_pattern, prompt)
            subject_match = re.search(subject_pattern, prompt, re.IGNORECASE)
            
            if not email_match:
                logger.error("No email address found in prompt")
                return None
                
            recipient = email_match.group(0)
            subject = subject_match.group(1).strip() if subject_match else "No Subject"
            
            # Use Gemini to generate content
            content_prompt = f"""
            Generate a professional email content based on the following request:
            {prompt}
            
            Requirements:
            - Keep the tone professional and engaging
            - Structure the content with clear paragraphs
            - Include relevant details and context
            - End with a clear call to action or conclusion
            """
            
            response = self.email_sender.model.generate_content(content_prompt)
            if not response or not response.text:
                logger.error("Failed to generate content from Gemini")
                return None
                
            # Create the email details dictionary
            email_details = {
                "recipient": recipient,
                "subject": subject,
                "content_prompt": response.text,
                "template_id": None  # Optional template ID
            }
            
            logger.info(f"Successfully parsed email details: {json.dumps(email_details, indent=2)}")
            return email_details
            
        except Exception as e:
            logger.error(f"Error parsing prompt: {str(e)}")
            return None

def main():
    """Main function to demonstrate the EmailAgent usage."""
    try:
        agent = EmailAgent()
        
        # Example usage
        print("Welcome to the Email Agent!")
        print("Please enter your email prompt (or 'x' to exit):")
        print("\nExample format:")
        print("send a mail to example@email.com subject:Your Subject content:Your message content")
        
        while True:
            user_prompt = input("\nYour prompt: ").strip()
            
            if user_prompt.lower() == 'x':
                print("Goodbye!")
                break
                
            success, message = agent.process_user_prompt(user_prompt)
            print(f"\nStatus: {'Success' if success else 'Failed'}")
            print(f"Message: {message}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 