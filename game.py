from aiogram.fsm.state import StatesGroup, State

tasks: list[str] = [
    "Первый",
    "Второй",
    "Третий",
    "Четвертый",
    "Пятый",
    "Шестой",
    "Седьмой",
    "Восьмой",
]


def get_points_from_answer(answer: str) -> int:
    if len(answer) < 2:
        return 0
    key_letter = answer[1].toLowerCase()
    match key_letter:
        case "у":
            return 0
        case "и":
            return 1
        case "е":
            return 2
        case "а":
            return 3
        case "о":
            return 4
        case "п":
            return 5
        case _:
            return 0


class GameState(StatesGroup):
    name_collection = State()
    task_selection = State()
    task_reply = State()
