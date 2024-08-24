from aiogram.fsm.state import StatesGroup, State

tasks: list[str] = [
    "Первый",
    "Второй",
    "Третий",
    "Четвертый",
    # "Пятый",
    # "Шестой",
    # "Седьмой",
    # "Восьмой",
    # "Девятый",
]


def get_points_from_answer(answer: str) -> int:
    if answer[0] == "А":
        return 5
    if answer[-1] == "О":
        return 4
    if answer[0] == "О":
        return 3
    if answer[-1] == "А":
        return 2
    if answer[1] == "Б":
        return 1
    return 0


class GameState(StatesGroup):
    name_collection = State()
    task_selection = State()
    task_reply = State()
