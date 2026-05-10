import datetime
from zoneinfo import ZoneInfo
from discord import Message
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

from utils.config import GOOGLE_SHEETS_API_JSON_FILE_PATH, GOOGLE_SPREADSHEET_ID

MANILA_TIMEZONE = ZoneInfo('Asia/Manila')

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

    print(f'Created new sheet')

    return response['replies'][0]['addSheet']['properties']['sheetId']

def initialize_sheet(service: Resource, sheet_title: str, forum_link: str, sheet_id: int):
    FULL_CELL_RANGE = f"'{sheet_title}'!A1:H4"
    VALUES = [
        [f'{sheet_title}'],
        ['DATE', f'{datetime.datetime.now().astimezone(MANILA_TIMEZONE).strftime("%d/%m/%Y")}'],
        ['FORUM LINK', forum_link],
        ['Timestamp Created', 'Last Edited', 'Message Link', 'Author', 'Raw Post', 'Edited Post', 'Notes', 'Status']
    ]

    # Add metadata and column headers
    service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        range=FULL_CELL_RANGE,
        valueInputOption='USER_ENTERED',
        body={
           'values': VALUES 
        }
    ).execute()

    # Make post and notes columns wider and wrap around; make status column a dropdown
    service.spreadsheets().batchUpdate(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        body={
            'requests': [
                {
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 4,
                            'endIndex': 7
                        },
                        'properties': {
                            'pixelSize': 400
                        },
                        'fields': 'pixelSize'
                    }
                },
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 4,
                            'endColumnIndex': 7,
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'wrapStrategy': 'WRAP'
                            }
                        },
                        'fields': 'userEnteredFormat.wrapStrategy'
                    }
                },
                {
                    'setDataValidation': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 7,
                            'endColumnIndex': 8,
                            'startRowIndex': 4,
                            'endRowIndex': 100
                        },
                        'rule': {
                            'condition': {
                                'type': 'ONE_OF_LIST',
                                'values': [{'userEnteredValue': option} for option in ('FOR EDITING', 'FOR POSTING', 'POSTED', 'DELETED')]
                            },
                            'showCustomUi': True,
                            'strict': True,
                            'inputMessage': 'Status'
                        }
                    }
                }
            ]
        }
    ).execute()

    print(f'Initialized sheet')

def add_sheet_entry(service: Resource, sheet_title: str, message: Message):
    # TODO: Handle editing, deletion, status
    CELL_RANGE = f"'{sheet_title}'!A1"
    VALUES = [
        [
            message.created_at.astimezone(MANILA_TIMEZONE).strftime('%H:%M:%S.%f'),
            '',
            message.jump_url,
            message.author.name,
            message.content
            '',
            '',
            'FOR EDITING'
        ]
    ]

    service.spreadsheets().values().append(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        range=CELL_RANGE,
        valueInputOption='USER_ENTERED',
        body={
           'values': VALUES 
        }
    ).execute()

    print(f'Added entry to sheet')