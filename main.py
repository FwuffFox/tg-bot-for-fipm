import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from QuizState import QuizState, get_random_task

# Bot token can be obtained via https://t.me/BotFather
env_token = getenv("BOT_TOKEN")
if not env_token:
    logging.error("BOT_TOKEN is not set")
    sys.exit(1)

TOKEN = str(env_token)

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.set_state(QuizState.name_collection)
    await message.answer("Введите группу (Например ПИ-2401):")


@dp.message(QuizState.name_collection)
async def collect_name_and_start_game(message: Message, state: FSMContext) -> None:
    await state.set_state(QuizState.question)
    await state.update_data(
        name=message.text, current_task=get_random_task(), finished_tasks=set()
    )

    logging.info(f"Группа {message.text} начала игру.")
    await ask_question(message, state)


async def ask_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data["i"] >= len(QuizState.questions):
        await message.answer(f"{html.bold("Вы завершили игру.")}")
        logging.info(f"Пользователь {data["name"]} завершил игру.")
        await state.clear()
        return

    await message.answer(get_question(data["i"]).question)


@dp.message(QuizState.question)
async def check_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    question = get_question(data["i"])
    if not question.is_correct(message.text):
        await message.answer(f"Неверно! Попробуй ещё раз!")
        return

    await message.answer("Верно!")
    data["i"] += 1
    logging.info(f"Пользователь {data["name"]} ответил верно на вопрос {data["i"]}.")
    await ask_question(message, state)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
