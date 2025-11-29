import os.path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Optional

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveService:
    def __init__(self, service_account_file: str):
        self.service_account_file = service_account_file
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API using Service Account"""
        try:
            if os.path.exists(self.service_account_file):
                self.creds = Credentials.from_service_account_file(
                    self.service_account_file, scopes=SCOPES)
                self.service = build('drive', 'v3', credentials=self.creds)
                print("✅ Google Drive authentication successful")
            else:
                print(f"⚠️ Service account file not found: {self.service_account_file}")
                self.service = None
        except Exception as e:
            print(f"❌ Google Drive authentication failed: {str(e)}")
            self.service = None

    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Path to the local file
            folder_id: ID of the folder to upload to (optional)
            
        Returns:
            File ID if successful, None otherwise
        """
        if not self.service:
            print("❌ Google Drive service not initialized")
            return None

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        try:
            file_name = os.path.basename(file_path)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(file_path, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            print(f"✅ File uploaded to Drive. File ID: {file.get('id')}")
            return file.get('id')

        except Exception as e:
            print(f"❌ Error uploading file to Drive: {str(e)}")
            return None
