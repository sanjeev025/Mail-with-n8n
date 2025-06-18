# AI-Powered Email Assistant

This project provides an intelligent email automation system that uses Google's Gemini AI to generate professional email content and n8n for reliable email delivery.

## Features

- 🤖 AI-powered email content generation using Google's Gemini 1.5
- 📧 Automated email sending through n8n workflow
- 📝 Support for email templates
- 🎯 Smart prompt parsing and context understanding
- 🔒 Secure credential management
- 📋 Rich text (HTML) email support
- 🎨 Customizable email styling
- 📊 Email tracking and logging

## Prerequisites

- Python 3.8+
- n8n installed locally or hosted instance
- Gmail account with App Password enabled
- Google API key for Gemini AI

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd Mail-with-n8n
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key
EMAIL_ADDRESS=your_gmail_address
EMAIL_PASSWORD=your_16_digit_app_password
N8N_WEBHOOK_URL=your_localhost_n8n_webhook_url
N8N_API_KEY=your_n8n_api_key
```

## n8n Setup

1. Start n8n:
```bash
n8n start
```

2. In the n8n workspace:
   - Create a new workflow
   - Add a Webhook node (POST method)
   - Add an Email node with the following configuration:
     - Resource: Message
     - Operation: Send
     - To: {{ $json.body.recipient }}
     - Subject: {{ $json.body.subject }}
     - Email Type: HTML
     - Message: {{ $json.body.content }}

## Usage

Run the email agent:
```bash
python mail-agent.py
```

Example prompts:
```
send a professional follow-up email to john@example.com subject:Meeting Follow-up regarding our discussion about the project timeline

send a thank you note to sarah@example.com subject:Thank You for Your Presentation expressing appreciation for yesterday's presentation

send a project update to team@example.com subject:Weekly Project Status summarizing the progress we made this week
```

## Security Notes

- Never commit your `.env` file
- Use App Passwords for Gmail authentication
- Regularly rotate your API keys
- Monitor email sending logs for unusual activity

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.
 
