import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from src.tools import fetch_unread_emails

# 1. Load environment variables & initialize AI
load_dotenv()
client = Groq()

# 2. Configure the Streamlit page
st.set_page_config(page_title="AI Email Assistant", page_icon="📧", layout="centered")

# Initialize session state variables so the app "remembers" them
if "emails" not in st.session_state:
    st.session_state.emails = None
if "email_content_for_ai" not in st.session_state:
    st.session_state.email_content_for_ai = ""

# 3. Build the User Interface
st.title("📧 AI Email Assistant")
st.subheader("Welcome! Fetch and analyze your unread emails using **Llama 3.1**.")

# Slider for number of emails
num_emails = st.sidebar.slider("Number of emails to fetch", min_value=1, max_value=10, value=3)

# 4. Fetch Action
if st.button("Fetch Emails", type="primary"):
    with st.spinner("Fetching unread emails from Gmail..."):
        # Fetch and save to session state memory
        st.session_state.emails = fetch_unread_emails(max_results=num_emails)
        
        # Prepare the text for the AI and save to session state
        st.session_state.email_content_for_ai = ""
        if st.session_state.emails:
            for i, email in enumerate(st.session_state.emails, 1):
                st.session_state.email_content_for_ai += f"\nEmail {i}:\nFrom: {email['Sender']}\nSubject: {email['Subject']}\nSnippet: {email['Snippet']}\n{'-'*20}"

# 5. Display Emails and AI Tools (Only if emails exist in memory)
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

        # --- AI ACTIONS (Side-by-side buttons) ---
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Summarize & Categorize"):
                with st.spinner("Llama 3.1 is analyzing your emails..."):
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
                        model="llama-3.1-8b-instant",
                    )
                    st.subheader("AI Agent Summary")
                    st.markdown(response1.choices[0].message.content)

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
                        model="llama-3.1-8b-instant",
                    )
                    st.subheader("AI Drafted Responses")
                    st.markdown(response2.choices[0].message.content)