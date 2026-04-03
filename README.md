# 📧 AI Email Triage Assistant

An automated, intelligent AI agent built with Python that connects to a Gmail account, fetches unread emails, and uses the **Llama 3.1** Large Language Model (via Groq API) to automatically categorize and summarize them.

This project demonstrates the practical application of API integration, OAuth 2.0 authentication, and Prompt Engineering to solve a real-world productivity problem.

## Key Features
* **Automated Email Fetching:** Integrates directly with the Gmail API to retrieve unread messages.
* **AI-Powered Summarization:** Uses Meta's blazing-fast Llama 3.1 model to read and understand email content.
* **Smart Categorization:** Automatically assigns context-aware tags to emails (e.g., Urgent, Work, Personal, Newsletter).
* **Secure Credential Management:** Implements `.env` files and `.gitignore` to securely handle API keys and OAuth tokens.

## Tech Stack
* **Language:** Python 3.12
* **AI Model:** Llama 3.1 (8B) hosted on Groq
* **APIs:** Google Client Library (Gmail API v1), Groq API
* **Libraries:** `google-auth-oauthlib`, `google-api-python-client`, `groq`, `python-dotenv`

## How to Run Locally

### 1. Clone the repository
```bash

git clone [https://github.com/YOUR-USERNAME/AI-Email-Assistant.git](https://github.com/YOUR-USERNAME/AI-Email-Assistant.git)
cd AI-Email-Assistant

```

### 2. Set up a virtual environment
```bash

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```
### 3. Install dependencies
```bash

pip install -r requirements.txt

```
### 4. Setup API Keys
1. Create a .env file in the root directory.
2. Add your Groq API key: GROQ_API_KEY=your_groq_api_key_here
3. Place your Google OAuth 2.0 credentials.json file in the root directory.

### 5. Run the Agent
```bash
python app.py
(On the first run, a browser window will open asking you to authenticate with your Google Account).

```
