import os
import datetime
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

def authenticate_sheets_api() -> Resource:
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SHEETS_API_JSON_FILE_PATH,
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    print('Completed setup of Google Sheets API')
    return service

def create_sheet(service: Resource, sheet_title: str):
    body = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': sheet_title,
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

    print(f'Created new sheet: {response = }')

    return response

def initialize_sheet(service: Resource, sheet_title: str, forum_link: str):
    CELL_RANGE = f"'{sheet_title}'!A1:H4"
    VALUES = [
        [f'{sheet_title}'],
        ['DATE', f'{datetime.datetime.now().strftime("%d/%m/%Y")}'],
        ['FORUM LINK', forum_link],
        ['Timestamp', 'Last Edited', 'Message Link', 'Author', 'Raw Post', 'Edited Post', 'Status', 'Notes']
    ]

    response = service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        range=CELL_RANGE,
        valueInputOption='USER_ENTERED',
        body={
           'values': VALUES 
        }
    ).execute()

    print(f'Initialized sheet: {response = }')

    return response