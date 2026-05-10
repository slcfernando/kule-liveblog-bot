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
    FULL_CELL_RANGE = f"'{sheet_title}'!A1:I4"
    VALUES = [
        [f'{sheet_title}'],
        ['DATE', f'{datetime.datetime.now().astimezone(MANILA_TIMEZONE).strftime("%d/%m/%Y")}'],
        ['FORUM LINK', forum_link],
        ['Message ID', 'Timestamp Created', 'Last Edited', 'Message Link', 'Author', 'Raw Post', 'Edited Post', 'Notes', 'Status']
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

    # Adjust formatting of initialized sheet
    service.spreadsheets().batchUpdate(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        body={
            'requests': [
                # Make post and notes columns wider
                {
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 5,
                            'endIndex': 8
                        },
                        'properties': {
                            'pixelSize': 400
                        },
                        'fields': 'pixelSize'
                    }
                },
                # Make post and notes columns wrap around
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 5,
                            'endColumnIndex': 8,
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'wrapStrategy': 'WRAP'
                            }
                        },
                        'fields': 'userEnteredFormat.wrapStrategy'
                    }
                },
                # Add dropdowns for status
                {
                    'setDataValidation': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 8,
                            'endColumnIndex': 9,
                            'startRowIndex': 4,
                            'endRowIndex': 1000
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
                },
                # Make the message ID column plaintext
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 1,
                            'endColumnIndex': 2,
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'numberFormat': {
                                    'type': 'TEXT'
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.numberFormat'
                    }
                },
            ]
        }
    ).execute()

    print(f'Initialized sheet')

def add_sheet_entry(service: Resource, sheet_title: str, message: Message):
    CELL_RANGE = f"'{sheet_title}'!A1"
    VALUES = [
        [
            str(message.id),
            message.created_at.astimezone(MANILA_TIMEZONE).strftime('%H:%M:%S'),
            '',
            message.jump_url,
            message.author.name,
            message.content,
            '',
            '',
            'FOR EDITING',
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

def find_row_by_message_id(service: Resource, sheet_title: str, id_to_search: str) -> int | None:
    result = (service.spreadsheets()
                      .values()
                      .get(spreadsheetId=GOOGLE_SPREADSHEET_ID, range=f"{sheet_title}!A5:A")
                      .execute()
            )
    rows = result.get('values', [])
    if not rows:
        print(f'No data rows yet in {sheet_title}')
        return None
    
    messageIds = [row[0] for row in rows]
    for index, messageId in enumerate(messageIds):
        if messageId == id_to_search:
            # hardcoded 5, because the actual rows of data start from row 5
            return index + 5

    return None

def edit_sheet_entry(service: Resource, sheet_title: str, message_id: str, new_message: Message):
    row_to_edit = find_row_by_message_id(service, sheet_title, message_id)
    if row_to_edit is None:
        print('The row to edit in the spreadsheet does not exist.')
        return None

    # Modify Last Edited column
    service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        range=f"'{sheet_title}'!C{row_to_edit}",
        valueInputOption='USER_ENTERED',
        body={
           'values': [
               [f'{datetime.datetime.now().astimezone(MANILA_TIMEZONE).strftime('%H:%M:%S')}']
           ] 
        }
    ).execute()

    # Modify Raw Post column
    service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SPREADSHEET_ID,
        range=f"'{sheet_title}'!F{row_to_edit}",
        valueInputOption='USER_ENTERED',
        body={
           'values': [
               [new_message.content]
           ] 
        }
    ).execute()