if (!(Test-Path -Path "./.venv")) {
    "Venv не найден. Установка библиотек"
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

    "Запуск"
    python "./tg_bot_fipm/main.py"
} else {
    "Venv найден."
    .venv\Scripts\activate
    "Запуск"
    python "./tg_bot_fipm/main.py"
}