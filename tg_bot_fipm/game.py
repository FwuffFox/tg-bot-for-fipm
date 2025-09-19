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
    tasks: dict[int, int]
    time_start: str
    time_end: str

    def __init__(self, name: str, handle: str, id: int):
        self.id = id
        self.handle = handle
        self.name = name
        self.tasks = dict[int, int]()

    def fixate_start_time(self) -> None:
        self.time_start = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))

    def fixate_end_time(self) -> None:
        self.time_end = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))


tasks: list[str] = [
    "Вход в Межпространство",
    "Столкновение миров", 
    "Танцевальный взрыв", 
    "Цифровой облик", 
    "Космический пиар", 
    "Чт0 быLO d@льш3?", 
    "Провода Галактики" 
    "Ярость Капитана",
    "Искажённый архив",
    "Экипаж на связи!"
]

groups_that_started = []
current_players: set[int] = set()


def get_points_from_answer(answer: str) -> int:
    if len(answer) < 4:
        return 0
    key_letter = answer[3].lower()
    match key_letter:
        case "а":
            return 0
        case "е":
            return 1
        case "и":
            return 2
        case "р":
            return 3
        case "у":
            return 4
        case "м":
            return 5
        case _:
            return 0
