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

# 3. Build the User Interface
st.title("📧 AI Email Assistant")
st.subheader("Welcome! Click the button below to fetch and analyze your unread emails using **Llama 3.1**.")
st.write("I will give you a quick summary of your unread emails and categorize them for you.")

# Δημιουργούμε το slider. Επιλέγει από 1 έως 10 emails. Ξεκινάει στο 3.
num_emails = st.sidebar.slider("Number of emails to fetch", min_value=1, max_value=10, value=3)

# 4. Create an action button
if st.button("Fetch & Analyze Emails", type="primary"):
    
    # st.spinner shows a loading animation while the code runs!
    with st.spinner("Fetching unread emails from Gmail..."):
        emails = fetch_unread_emails(max_results=num_emails)
    
    if not emails:
        st.success("Your inbox is clean! No unread emails found. ")
    else:
        st.info(f"Found {len(emails)} unread email(s).")
        
        email_content_for_ai = ""
        
        # Display each email in a nice expandable box (expander)
        st.subheader("📥 Inbox Preview")
        for i, email in enumerate(emails, 1):
            email_content_for_ai += f"\nEmail {i}:\nFrom: {email['Sender']}\nSubject: {email['Subject']}\nSnippet: {email['Snippet']}\n{'-'*20}"
            
            with st.expander(f"Email {i}: {email['Subject']} (From: {email['Sender']})"):
                st.write(f"**Snippet:** {email['Snippet']}")

        # 5. Send to AI for Analysis
        with st.spinner("🧠 Llama 3.1 is analyzing your emails..."):
            system_prompt = """
            You are a highly efficient AI Email Assistant. 
            Your task is to read the provided unread emails and for each one:
            1. Assign a category (Urgent, Work, Personal, Spam, Newsletter, bills).
            2. Provide a very brief, 1-sentence summary of what the email is about.
            
            Format your response clearly using Markdown (use bold text for categories and bullet points). Always reply in English.
            """

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here are my latest unread emails:\n{email_content_for_ai}"}
                ],
                model="llama-3.1-8b-instant",
            )

        # 6. Display the final AI response
        st.subheader("AI Agent Summary & Categorization")
        st.markdown(response.choices[0].message.content)



