import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from game import GameState, get_points_from_answer, tasks
from result_writer import write_result

env_token = getenv("BOT_TOKEN")
if not env_token:
    logging.error("BOT_TOKEN is not set")
    sys.exit(1)

TOKEN = str(env_token)

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(GameState.name_collection)

    await message.answer("Приветствие")
    await message.answer("Введите группу которую вы представляете (Например ПИ-2401):")


@dp.message(GameState.name_collection)
async def collect_name_and_start_game(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Введите название группы!")
        return

    await state.update_data(group=message.text)
    logging.info(f"Группа {message.text} начала игру.")

    await display_tasks(message, state)


async def display_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    answered_tasks = data.get("answered_tasks", {})

    buttons: list[list[InlineKeyboardButton]] = [[]]
    cur_row: list[InlineKeyboardButton] = buttons[0]
    for i, task in enumerate(tasks):
        if i in answered_tasks:
            continue
        if len(cur_row) == 3:
            buttons.append([])
            cur_row = buttons[-1]
        cur_row.append(InlineKeyboardButton(text=task, callback_data=f"{i}"))

    if len(buttons[0]) == 0:
        await process_end_game(message, state)
        return

    await message.answer(
        text="Выберите задание:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )

    await state.set_state(GameState.task_selection)


@dp.callback_query(GameState.task_selection)
async def task_selection_handler(query: CallbackQuery, state: FSMContext) -> None:
    selection = query.data
    if selection is None or not selection.isdigit():
        return

    cur_task = int(selection)
    await state.update_data(cur_task=cur_task)
    await state.set_state(GameState.task_reply)

    await query.message.answer("Введите ответ полученный у куратора!")  # type: ignore


@dp.message(GameState.task_reply)
async def process_task_reply(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    answered_tasks = data.get("answered_tasks", {})
    cur_task = int(data["cur_task"])
    if cur_task in answered_tasks:
        await message.answer("(ОШИБКА) Вы уже ответили на это задание!")
        await display_tasks(message, state)
        return

    if not message.text:
        await message.answer("Введите ответ полученный у куратора!")
        return

    points = get_points_from_answer(message.text)
    answered_tasks[cur_task] = points
    await state.update_data(answered_tasks=answered_tasks)

    await state.set_state(GameState.task_selection)

    await message.answer(
        f"{html.bold("УБРАТЬ ПОСЛЕ ТЕСТИРОВАНИЯ")}\n"
        + f"Вы получили {points} баллов за задание {tasks[cur_task]}\n"
        + f"Текущие результаты: {answered_tasks}"
    )

    await display_tasks(message, state)


async def process_end_game(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    answered_tasks = data.get("answered_tasks", {})
    total_points = sum(answered_tasks.values())

    await message.answer(
        f"Игра окончена! Ваш результат: {total_points} баллов."
        + f"Полученные баллы за задания: {answered_tasks}"
    )

    write_result(data["group"], answered_tasks)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
