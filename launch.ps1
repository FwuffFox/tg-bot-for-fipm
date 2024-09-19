if (!(Test-Path -Path "./.venv")) {
    "Venv не найден. Установка пакетов."
    python -m venv .venv
    ./.venv/Scripts/Activate.ps1
    pip install -r requirements.txt

    "Запуск"
    python "./tg_bot_fipm/main.py"
} else {
    "Venv найден."
    ./.venv/Scripts/Activate.ps1
    "Запуск"
    python "./tg_bot_fipm/main.py"
}