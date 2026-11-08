import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_email_body(payload):
    """
    Recursively searches the Gmail API payload to find and decode the plain text body.
    """
    # If this specific part is plain text, decode and return it
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            # Decoding Google's encoded text 
            return base64.urlsafe_b64decode(data).decode("utf-8")
        return ""
    
    # If the email has multiple parts search further
    if "parts" in payload:
        for part in payload["parts"]:
            text = get_email_body(part)
            if text:
                return text
                
    return "No readable text found."

# Allow OAuth authentication over HTTP for local development and testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Request read-only access to the user's Gmail account
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def fetch_unread_emails(max_results=3):
    """
    Fetches the latest unread emails from the user's Gmail account.
    Returns a list of dictionaries containing 'Sender', 'Subject', and 'Snippet'.
    """
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no credentials available, let the user log in but if there are expired ones refresh them.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost'
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n" + "="*60)
            print("1. PLEASE CLICK THIS LINK TO AUTHENTICATE WITH GOOGLE:")
            print(auth_url)
            print("="*60 + "\n")
            
            response_url = input("2. PASTE THE FAILED LOCALHOST URL HERE and press Enter: ")
            
            flow.fetch_token(authorization_response=response_url.strip())
            creds = flow.credentials
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Create the Gmail API Client
    service = build('gmail', 'v1', credentials=creds)
    
    # Fetch unread messages
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
    messages = results.get('messages', [])

    email_data_list = []

    if not messages:
        return email_data_list # Returns empty list if no unread emails

    # Extract details for each email
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])
        
        full_text = get_email_body(payload)
         
        limit_text = full_text[:1500] 

        # Get the Subject and Sender from the headers
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        
        # Store in a dictionary
        email_data_list.append({
            "Sender": sender,
            "Subject": subject,
            "Snippet": limit_text # Passing up to 1500 characters of the real email
        })
    return email_data_list
