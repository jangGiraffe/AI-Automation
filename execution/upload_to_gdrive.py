import os
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

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

def create_folder(service, folder_name, parent_id):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    try:
        file = service.files().create(body=file_metadata,
                                    fields='id').execute()
        print(f"Created folder: {folder_name} (ID: {file.get('id')})")
        return file.get('id')
    except Exception as e:
        print(f"Error creating folder {folder_name}: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: py upload_to_gdrive.py <local_folder_path> <drive_parent_folder_id>")
        sys.exit(1)

    local_folder_path = sys.argv[1]
    drive_parent_folder_id = sys.argv[2]
    
    if not os.path.exists(local_folder_path):
        print(f"Error: Local path {local_folder_path} does not exist.")
        sys.exit(1)

    service = get_service()
    if not service:
        sys.exit(1)

    # Create a folder on Drive with the same name as the local folder
    folder_name = os.path.basename(os.path.normpath(local_folder_path))
    new_drive_folder_id = create_folder(service, folder_name, drive_parent_folder_id)
    
    if not new_drive_folder_id:
        print("Failed to create parent folder on Drive.")
        sys.exit(1)

    # Upload files in the directory
    for root, dirs, files in os.walk(local_folder_path):
        # Flattened upload for simplicity, or maintain structure? 
        # For this specific task, we just want the files in the date folder.
        # But if there are subdirectories, we should probably handle them. 
        # For now, let's assume a flat structure inside the date folder as per previous output.
        
        for filename in files:
            file_path = os.path.join(root, filename)
            # Determine mime type optionally, or let Google Drive detect
            upload_file(service, file_path, new_drive_folder_id)

    print("Upload completed.")

if __name__ == '__main__':
    main()
