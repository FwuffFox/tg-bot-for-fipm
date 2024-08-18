import random
from aiogram.fsm.state import StatesGroup, State


class Task:
    question: str
    answer: str

    def __init__(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer

    def is_correct(self, answer: str) -> bool:
        return self.answer.lower() == answer.lower()


class QuizState(StatesGroup):
    name_collection = State()
    question = State()


tasks: list[Task] = [
    Task("Сколько будет 2+2?", "4"),
    Task("Сколько будет 2*2?", "4"),
    Task("Сколько будет 2**3?", "8"),
]


def get_random_task() -> Task:
    return random.choice(tasks)
