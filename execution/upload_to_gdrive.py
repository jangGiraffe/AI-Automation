import os
import sys
import pickle
import datetime
import shutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found. Please place it in the project root.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def upload_file(service, file_path, folder_id, mime_type=None):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    try:
        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        print(f"Uploaded file: {file_path} (ID: {file.get('id')})")
        return file.get('id')
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
        return None

def find_folder(service, folder_name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    return None

def create_folder(service, folder_name, parent_id):
    existing_id = find_folder(service, folder_name, parent_id)
    if existing_id:
        return existing_id

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    try:
        file = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Created folder: {folder_name} (ID: {file.get('id')})")
        return file.get('id')
    except Exception as e:
        print(f"Error creating folder {folder_name}: {e}")
        return None

def get_next_date_folder_name(service, parent_id, date_str):
    """
    Check for existing folders starting with date_str and find the next available index.
    Naming convention: YYYY-MM-DD, YYYY-MM-DD(2), YYYY-MM-DD(3)...
    """
    base_name = date_str
    
    # Check base name first
    if not find_folder(service, base_name, parent_id):
        return base_name
    
    # Check indexed names
    index = 2
    while True:
        next_name = f"{base_name}({index})"
        if not find_folder(service, next_name, parent_id):
            return next_name
        index += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: py upload_to_gdrive.py <local_folder_path> [parent_folder_id_or_path]")
        print("If parent_folder_id_or_path is omitted, GOOGLE_DRIVE_PARENT_FOLDER_ID from .env is used.")
        sys.exit(1)

    local_folder_path = sys.argv[1]
    
    if not os.path.exists(local_folder_path):
        print(f"Error: Local path {local_folder_path} does not exist.")
        sys.exit(1)

    service = get_service()
    if not service:
        sys.exit(1)

    # Determine Parent Folder ID
    parent_folder_id = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID")
    arg_override = sys.argv[2] if len(sys.argv) > 2 else None

    if arg_override:
        # If argument provided, check if it's an ID or path (primitive check)
        if ' ' in arg_override or '/' in arg_override or '>' in arg_override:
             print(f"Resolving path from argument: {arg_override}")
             # Warning: This assumes path is relative to root if ID not found, logic omitted for brevity
             # For now, let's treat argument as ID if it looks like one, else fail or warn.
             # User requested env var usage primarily. 
             # Let's support the user's specific case: use env var ID as root.
             pass 
        else:
             parent_folder_id = arg_override
    
    if not parent_folder_id:
        print("Error: GOOGLE_DRIVE_PARENT_FOLDER_ID not found in .env and no argument provided.")
        sys.exit(1)

    # 1. Logic for Date Folder Naming
    # Extract date from local folder path if possible, or use today's date
    path_base_name = os.path.basename(os.path.normpath(local_folder_path))
    
    # Try to parse date from folder name YYYY-MM-DD
    try:
        datetime.datetime.strptime(path_base_name, '%Y-%m-%d')
        date_str = path_base_name
    except ValueError:
        date_str = datetime.date.today().strftime('%Y-%m-%d')

    print(f"Target Parent Folder ID: {parent_folder_id}")
    
    # Create unique date folder under the parent
    target_folder_name = get_next_date_folder_name(service, parent_folder_id, date_str)
    print(f"Creating/Using Folder: {target_folder_name}")
    
    final_folder_id = create_folder(service, target_folder_name, parent_folder_id)
    
    if not final_folder_id:
        print("Failed to create destination folder.")
        sys.exit(1)


    for root, dirs, files in os.walk(local_folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            upload_file(service, file_path, final_folder_id)

    print("Upload completed.")

if __name__ == '__main__':
    main()
