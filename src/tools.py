import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Disable https requirement for local testing in Codespaces
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# If modifying these scopes, delete the file token.json.
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
        
    # If there are no (valid) credentials available, let the user log in.
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

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Fetch unread messages
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
    messages = results.get('messages', [])

    email_data_list = []

    if not messages:
        return email_data_list # Returns empty list if no unread emails

    # Extract details for each email
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        snippet = msg_detail.get('snippet', '')
        
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        
        # Store in a dictionary
        email_data_list.append({
            "Sender": sender,
            "Subject": subject,
            "Snippet": snippet # This is the first few lines of the email body
        })

    return email_data_list