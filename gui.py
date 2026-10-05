import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from src.tools import fetch_unread_emails

# Load the API key from .env and create the AI client
load_dotenv()
client = Groq()

# Configure the Streamlit page
st.set_page_config(page_title="AI Email Assistant", page_icon="📧", layout="centered")

# Initialize session state variables so they survive Streamlit re-runs
if "emails" not in st.session_state:
    st.session_state.emails = None
if "email_content_for_ai" not in st.session_state:
    st.session_state.email_content_for_ai = ""

# Build the User Interface
st.title("📧 AI Email Assistant")
st.subheader("Welcome! Fetch and analyze your unread emails using **GPT-OSS 20B**.")

# Slider for number of emails
num_emails = st.sidebar.slider("Number of emails to fetch", min_value=1, max_value=10, value=3)

# Fetch Action
if st.button("Fetch Emails", type="primary"):
    with st.spinner("Fetching unread emails from Gmail..."):
        # Fetch and save to session state memory
        st.session_state.emails = fetch_unread_emails(max_results=num_emails)
        
        # Prepare the text for the AI and save to session state
        st.session_state.email_content_for_ai = ""
        if st.session_state.emails:
            for i, email in enumerate(st.session_state.emails, 1):
                st.session_state.email_content_for_ai += f"\nEmail {i}:\nFrom: {email['Sender']}\nSubject: {email['Subject']}\nSnippet: {email['Snippet']}\n{'-'*20}"

# Display Emails and AI Tools (Only if emails exist in memory)
if st.session_state.emails is not None:
    if len(st.session_state.emails) == 0:
        st.success("Your inbox is clean! No unread emails found. 🎈")
    else:
        st.info(f"Found {len(st.session_state.emails)} unread email(s).")
        
        # Display Inbox Preview
        st.subheader("📥 Inbox Preview")
        for i, email in enumerate(st.session_state.emails, 1):
            with st.expander(f"Email {i}: {email['Subject']} (From: {email['Sender']})"):
                st.write(f"**Snippet:** {email['Snippet']}")

        # AI ACTIONS (Side-by-side buttons)
        col1, col2 = st.columns(2)

        # Left column: summarize and categorize
        with col1:
            if st.button("📊 Summarize & Categorize"):
                with st.spinner("GPT-OSS 20B is analyzing your emails..."):
                    system_prompt1 = """
                    You are a highly efficient AI Email Assistant. 
                    Your task is to read the provided unread emails and for each one:
                    1. Assign a category (Urgent, Work, Personal, Spam, Newsletter, Bills).
                    2. Provide a very brief, 1-sentence summary.
                    
                    Format your response clearly using Markdown. Always reply in English.
                    """
                    response1 = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt1},
                            {"role": "user", "content": f"Here are my latest unread emails:\n{st.session_state.email_content_for_ai}"}
                        ],
                        model="openai/gpt-oss-20b",
                    )
                    st.subheader("AI Agent Summary")
                    st.markdown(response1.choices[0].message.content)

        # Right column: draft replies
        with col2:
            if st.button("✍️ Draft Responses"):
                with st.spinner("Thinking of a response..."):
                    system_prompt2 = """
                    You are a highly efficient AI Email Assistant. 
                    Your task is to read the provided unread emails and write a polite, professional response for each one that requires a reply. 
                    If an email is spam or a newsletter, skip it.
                    Format your response clearly. Always reply in English.
                    """
                    response2 = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt2},
                            {"role": "user", "content": f"Here are my latest unread emails:\n{st.session_state.email_content_for_ai}"}
                        ],
                        model="openai/gpt-oss-20b",
                    )
                    # Show the AI's reply as formatted text
                    st.subheader("AI Drafted Responses")
                    st.markdown(response2.choices[0].message.content)
