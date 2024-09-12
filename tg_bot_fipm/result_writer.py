from datetime import datetime, timezone
from os import getenv
from typing import Any
import game
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1-P-LfeMeIy2U9RBFOuQ1S8GLwVwuCzFU55oxzpo52Lg"
SHEET_NAME = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
SERVICE_ACCOUNT_FILE = getenv("SERVICE_ACCOUNT_FILE")

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("sheets", "v4", credentials=credentials)
sheet = service.spreadsheets()


def create_table():
    requests = [{"addSheet": {"properties": {"title": SHEET_NAME}}}]
    batch_update_request = {"requests": requests}
    sheet.batchUpdate(spreadsheetId=SHEET_ID, body=batch_update_request).execute()
    print(f"Новый лист создан: {SHEET_NAME}. ID: {SHEET_ID}")

    append_rows(
        [
            [
                "ID",
                "Хэндл",
                "Имя",
                *game.tasks,
                "Сумма баллов",
                "Время Начала",
                "Время Окончания",
            ]
        ]
    )


def write(player_data: game.PlayerData):
    append_rows(
        [
            [player_data.id, player_data.handle, player_data.name]
            + [player_data.tasks.get(i, 0) for i in range(len(game.tasks))]
            + [sum(player_data.tasks.values())]
            + [player_data.time_start, player_data.time_end]
        ]
    )


def append_rows(rows: list[Any]):
    sheet.values().append(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A:A",
        valueInputOption="RAW",
        body={"values": rows},
        insertDataOption="INSERT_ROWS",
    ).execute()


# Example usage:
create_table()
