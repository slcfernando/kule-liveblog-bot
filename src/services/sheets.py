import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

# Get environment variables needed for Google Sheets API
load_dotenv()

GOOGLE_SHEETS_API_JSON_FILE_PATH = os.getenv('GOOGLE_SHEETS_API_JSON_FILE_PATH')
GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')

SCOPES = (
    'https://www.googleapis.com/auth/spreadsheets',
    )

def connect_to_sheets_api() -> Resource:
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SHEETS_API_JSON_FILE_PATH,
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def create_sheet(service: Resource, title: str):
    body = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': title,
                        'index': 0
                    }
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        body=body
    ).execute()

    return response