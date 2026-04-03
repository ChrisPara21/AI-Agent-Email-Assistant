import os
from dotenv import load_dotenv
from groq import Groq

# Import our custom Gmail tool
from src.tools import fetch_unread_emails

# Load environment variables
load_dotenv()

# Initialize the AI Agent (Groq automatically finds the key in .env)
client = Groq()

def main():
    print("1. Fetching unread emails from Gmail...")
    
    # Use our tool to get the 3 latest emails
    emails = fetch_unread_emails(max_results=3)

    if not emails:
        print("Your inbox is clean! No unread emails found.")
        return

    print(f"Found {len(emails)} unread email(s). Analyzing with Llama 3.1...\n")

    # Format the emails into a single text block for the AI to read
    email_content_for_ai = ""
    for i, email in enumerate(emails, 1):
        email_content_for_ai += f"\nEmail {i}:\nFrom: {email['Sender']}\nSubject: {email['Subject']}\nSnippet: {email['Snippet']}\n{'-'*20}"

    # The System Prompt: Giving instructions to our Agent
    system_prompt = """
    You are a highly efficient AI Email Assistant. 
    Your task is to read the provided unread emails and for each one:
    1. Assign a category (e.g., Urgent, Work, Personal, Spam, Newsletter).
    2. Provide a very brief, 1-sentence summary of what the email is about.
    
    Format your response clearly and profecionaly. Always reply in English.
    """

    # Send the instructions and the emails to Groq
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here are my latest unread emails:\n{email_content_for_ai}"}
        ],
        model="llama-3.1-8b-instant",
    )

    print("=== AI AGENT SUMMARY & CATEGORIZATION ===")
    print(response.choices[0].message.content)
    print("=========================================\n")

if __name__ == "__main__":
    main()