import time
from aiogram.fsm.state import StatesGroup, State


class GameState(StatesGroup):
    name_collection = State()
    task_selection = State()
    task_reply = State()


class PlayerData:
    id: int = -1
    handle: str = ""
    name: str = ""
    cur_task: int = -1
    tasks: dict[int, int] = {}
    time_start: str = ""
    time_end: str = ""

    def __init__(self, name: str, handle: str, id: int):
        self.id = id
        self.handle = handle
        self.name = name

    def fixate_start_time(self) -> None:
        self.time_start = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))

    def fixate_end_time(self) -> None:
        self.time_end = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))


tasks: list[str] = [
    "Станция 1",
    "Станция 2",
    "Cтанция 3",
    "Станция 4",
    "Станция 5",
    "Станция 6",
    "Станция 7",
    "Станция 8",
    "Доп. задание 1",
    "Доп. задание 2",
]

groups_that_started = []
current_players: set[int] = set()


def get_points_from_answer(answer: str) -> int:
    if len(answer) < 2:
        return 0
    key_letter = answer[1].lower()
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
