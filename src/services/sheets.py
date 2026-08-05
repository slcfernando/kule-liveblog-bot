import datetime
import json
import os
import time
from zoneinfo import ZoneInfo

from discord import Message
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from utils.config import GOOGLE_SHEETS_API_JSON_FILE_PATH, GOOGLE_SPREADSHEET_ID

assert GOOGLE_SHEETS_API_JSON_FILE_PATH is not None
assert GOOGLE_SPREADSHEET_ID is not None

MANILA_TIMEZONE = ZoneInfo("Asia/Manila")

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)


def execute_with_retry(request, retries: int = 3, delay: float = 2.0):
    """Execute a Google API request with simple retry logic."""
    for attempt in range(retries):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in (429, 500, 503) and attempt < retries - 1:
                print(
                    f"API error {e.resp.status}, retrying in {delay}s (attempt {attempt + 1}/{retries})"
                )
                time.sleep(delay)
            else:
                raise
        except Exception as e:
            if attempt < retries - 1:
                print(
                    f"Request failed: {e}, retrying in {delay}s (attempt {attempt + 1}/{retries})"
                )
                time.sleep(delay)
            else:
                raise


def authenticate_sheets_api() -> Resource:
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        # If on Railway, load from environment variable
        credentials_info = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES
        )
    else:
        # If local, load from file
        assert GOOGLE_SHEETS_API_JSON_FILE_PATH is not None
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_SHEETS_API_JSON_FILE_PATH, scopes=SCOPES
        )

    service = build("sheets", "v4", credentials=creds)
    print("Completed setup of Google Sheets API")
    return service


def create_sheet(service: Resource, sheet_title: str):
    body = {
        "requests": [{"addSheet": {"properties": {"title": sheet_title, "index": 0}}}]
    }

    response = execute_with_retry(
        service.spreadsheets().batchUpdate(
            spreadsheetId=GOOGLE_SPREADSHEET_ID, body=body
        )
    )

    print("Created new sheet")

    return response["replies"][0]["addSheet"]["properties"]["sheetId"]


def initialize_sheet(
    service: Resource, sheet_title: str, forum_link: str, sheet_id: int
):
    FULL_CELL_RANGE = f"'{sheet_title}'!A1:I4"
    VALUES = [
        [f"{sheet_title}"],
        [
            "DATE",
            f"{datetime.datetime.now().astimezone(MANILA_TIMEZONE).strftime('%d/%m/%Y')}",
        ],
        ["FORUM LINK", forum_link],
        [
            "Message ID",
            "Timestamp Created",
            "Last Edited",
            "Message Link",
            "Author",
            "Raw Post",
            "Edited Post",
            "Notes",
            "Status",
        ],
    ]

    # Add metadata and column headers
    execute_with_retry(
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            range=FULL_CELL_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": VALUES},
        )
    )

    # Adjust formatting of initialized sheet
    execute_with_retry(
        service.spreadsheets().batchUpdate(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            body={
                "requests": [
                    # Make post and notes columns wider
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 5,
                                "endIndex": 8,
                            },
                            "properties": {"pixelSize": 400},
                            "fields": "pixelSize",
                        }
                    },
                    # Make post and notes columns wrap around
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startColumnIndex": 5,
                                "endColumnIndex": 8,
                            },
                            "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}},
                            "fields": "userEnteredFormat.wrapStrategy",
                        }
                    },
                    # Add dropdowns for status
                    {
                        "setDataValidation": {
                            "range": {
                                "sheetId": sheet_id,
                                "startColumnIndex": 8,
                                "endColumnIndex": 9,
                                "startRowIndex": 4,
                                "endRowIndex": 1000,
                            },
                            "rule": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [
                                        {"userEnteredValue": option}
                                        for option in (
                                            "FOR EDITING",
                                            "FOR POSTING",
                                            "POSTED",
                                            "DELETED",
                                        )
                                    ],
                                },
                                "showCustomUi": True,
                                "strict": True,
                                "inputMessage": "Status",
                            },
                        }
                    },
                    # Make the message ID column plaintext
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startColumnIndex": 0,
                                "endColumnIndex": 1,
                            },
                            "cell": {
                                "userEnteredFormat": {"numberFormat": {"type": "TEXT"}}
                            },
                            "fields": "userEnteredFormat.numberFormat",
                        }
                    },
                    # Add color coding based on the status
                    {
                        "addConditionalFormatRule": {
                            "rule": {
                                "ranges": [
                                    {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 4,
                                        "endRowIndex": 1000,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 9,
                                    }
                                ],
                                "booleanRule": {
                                    "condition": {
                                        "type": "CUSTOM_FORMULA",
                                        "values": [
                                            {"userEnteredValue": '=$I5="FOR EDITING"'}
                                        ],
                                    },
                                    "format": {
                                        "backgroundColor": {
                                            "red": 0.96,
                                            "green": 0.86,
                                            "blue": 0.57,
                                        }
                                    },
                                },
                            },
                            "index": 0,
                        }
                    },
                    {
                        "addConditionalFormatRule": {
                            "rule": {
                                "ranges": [
                                    {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 4,
                                        "endRowIndex": 1000,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 9,
                                    }
                                ],
                                "booleanRule": {
                                    "condition": {
                                        "type": "CUSTOM_FORMULA",
                                        "values": [
                                            {"userEnteredValue": '=$I5="FOR POSTING"'}
                                        ],
                                    },
                                    "format": {
                                        "backgroundColor": {
                                            "red": 0.64,
                                            "green": 0.76,
                                            "blue": 0.96,
                                        }
                                    },
                                },
                            },
                            "index": 0,
                        }
                    },
                    {
                        "addConditionalFormatRule": {
                            "rule": {
                                "ranges": [
                                    {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 4,
                                        "endRowIndex": 1000,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 9,
                                    }
                                ],
                                "booleanRule": {
                                    "condition": {
                                        "type": "CUSTOM_FORMULA",
                                        "values": [
                                            {"userEnteredValue": '=$I5="POSTED"'}
                                        ],
                                    },
                                    "format": {
                                        "backgroundColor": {
                                            "red": 0.72,
                                            "green": 0.84,
                                            "blue": 0.66,
                                        }
                                    },
                                },
                            },
                            "index": 0,
                        }
                    },
                    {
                        "addConditionalFormatRule": {
                            "rule": {
                                "ranges": [
                                    {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 4,
                                        "endRowIndex": 1000,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 9,
                                    }
                                ],
                                "booleanRule": {
                                    "condition": {
                                        "type": "CUSTOM_FORMULA",
                                        "values": [
                                            {"userEnteredValue": '=$I5="DELETED"'}
                                        ],
                                    },
                                    "format": {
                                        "backgroundColor": {
                                            "red": 0.92,
                                            "green": 0.6,
                                            "blue": 0.6,
                                        }
                                    },
                                },
                            },
                            "index": 0,
                        }
                    },
                ]
            },
        )
    )

    print("Initialized sheet")


def add_sheet_entry(service: Resource, sheet_title: str, message: Message):
    CELL_RANGE = f"'{sheet_title}'!A1"
    VALUES = [
        [
            str(message.id),
            message.created_at.astimezone(MANILA_TIMEZONE).strftime("%H:%M:%S"),
            "",
            message.jump_url,
            message.author.name,
            message.content,
            "",
            "",
            "FOR EDITING",
        ]
    ]

    execute_with_retry(
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            range=CELL_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": VALUES},
        )
    )

    print("Added entry to sheet")


def find_row_by_message_id(
    service: Resource, sheet_title: str, id_to_search: str
) -> int | None:
    result = execute_with_retry(
        service.spreadsheets()
        .values()
        .get(spreadsheetId=GOOGLE_SPREADSHEET_ID, range=f"{sheet_title}!A5:A")
    )
    rows = result.get("values", [])
    if not rows:
        print(f"No data rows yet in {sheet_title}")
        return None

    for index, row in enumerate(rows):
        if row and row[0] == id_to_search:
            # hardcoded 5, because the actual rows of data start from row 5
            return index + 5

    print(f"Message ID {id_to_search} not found in {sheet_title}")
    return None


def edit_sheet_entry(
    service: Resource, sheet_title: str, message_id: str, new_message: Message
):
    row_to_edit = find_row_by_message_id(service, sheet_title, message_id)
    if row_to_edit is None:
        print("The row to edit in the spreadsheet does not exist.")
        return None

    execute_with_retry(
        service.spreadsheets()
        .values()
        .batchUpdate(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    # Modify Last Edited column
                    {
                        "range": f"'{sheet_title}'!C{row_to_edit}",
                        "values": [
                            [
                                f"{datetime.datetime.now().astimezone(MANILA_TIMEZONE).strftime('%H:%M:%S')}"
                            ]
                        ],
                    },
                    # Modify Raw Post column
                    {
                        "range": f"'{sheet_title}'!F{row_to_edit}",
                        "values": [[new_message.content]],
                    },
                ],
            },
        )
    )


def delete_sheet_entry(service: Resource, sheet_title: str, message: Message):
    row_to_delete = find_row_by_message_id(service, sheet_title, str(message.id))
    if row_to_delete is None:
        print("The row to delete in the spreadsheet does not exist.")
        return None

    execute_with_retry(
        service.spreadsheets()
        .values()
        .batchUpdate(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                        "range": f"'{sheet_title}'!I{row_to_delete}",
                        "values": [["DELETED"]],
                    }
                ],
            },
        )
    )

    print(f"Marked row {row_to_delete} as DELETED")


def get_last_message_id(service: Resource, sheet_title: str) -> str | None:
    result = execute_with_retry(
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            range=f"'{sheet_title}'!A5:A",
        )
    )
    print(f"{result = }")

    rows = result.get("values", [])
    if not rows:
        print("Rows seems to be empty.")
        return None

    for row in reversed(rows):
        print(f"{row = }")
        # TODO: Confirm if row[0] != "DELETED" is the correct change; diba last entry dapat?
        if row and row[0] and row[0] != "DELETED":
            return row[0]

    return None
