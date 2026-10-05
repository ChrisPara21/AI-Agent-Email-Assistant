# AI Email Triage Assistant

An automated, intelligent AI agent built with Python that connects to a Gmail account, fetches unread emails, and uses the **GPT-OSS 20B** Large Language Model (via Groq API) to automatically categorize and summarize them.

This project demonstrates the practical application of API integration, OAuth 2.0 authentication, and Prompt Engineering to solve a real-world productivity problem.

## Key Features
* **Automated Email Fetching:** Integrates directly with the Gmail API to retrieve unread messages.
* **AI-Powered Summarization:** Uses Meta's blazing-fast Llama 3.1 model to read and understand email content.
* **Smart Categorization:** Automatically assigns context-aware tags to emails (e.g., Urgent, Work, Personal, Newsletter).
* **Secure Credential Management:** Implements `.env` files and `.gitignore` to securely handle API keys and OAuth tokens.
