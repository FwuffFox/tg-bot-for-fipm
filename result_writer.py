import game  
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource

# Replace with your Google Sheet ID and sheet name
SHEET_ID = "1-P-LfeMeIy2U9RBFOuQ1S8GLwVwuCzFU55oxzpo52Lg"
SHEET_NAME = "Результаты"

# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = "botvuz-db1b38869eee.json"

# Authentication and API client setup
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("sheets", "v4", credentials=credentials)
sheet = service.spreadsheets()

def create_table():
    try:
        # clear table
        sheet.values().clear(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A:Z"
        ).execute()
    except:
        print(f"НЕТ ТАБЛИЦЫ {SHEET_NAME}")
        raise

    header = [["Имя"] + game.tasks + ["Сумма баллов"]]
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        body={"values": header}
    ).execute()

def write_result(name: str, answers: dict[int, int]):
    result = [name] + [answers.get(i, 0) for i in range(len(game.tasks))] + [sum(answers.values())]
    sheet.values().append(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A:A",
        valueInputOption="RAW",
        body={"values": [result]},
        insertDataOption="INSERT_ROWS"
    ).execute()

# Example usage:
create_table()