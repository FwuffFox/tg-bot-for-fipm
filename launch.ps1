if (!(Test-Path -Path "./.venv")) {
    "Venv не найден. Установка библиотек"
    python -m venv .venv
    ./.venv/bin/Activate.ps1
    pip install -r requirements.txt

    "Запуск"
    python "./tg_bot_fipm/main.py"
} else {
    "Venv найден."
    ./.venv/bin/Activate.ps1
    "Запуск"
    python "./tg_bot_fipm/main.py"
}