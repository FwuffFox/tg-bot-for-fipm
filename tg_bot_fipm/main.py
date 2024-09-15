import asyncio
import logging
import os
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import F, Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile
)

from game import (
    GameState,
    PlayerData,
    get_points_from_answer,
    tasks,
    groups_that_started,
    current_players,
)
import result_writer
import texts

load_dotenv(override=True)

env_token = getenv("BOT_TOKEN")
if not env_token:
    logging.error("BOT_TOKEN is not set")
    sys.exit(1)

TOKEN = str(env_token)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if message.chat.id in current_players or await state.get_state() is not None:
        await message.answer("Вы уже начали или прошли игру!")
        return

    await state.set_state(GameState.name_collection)

    await message.answer_photo(FSInputFile("img/start.png"), texts.GREETING)
    await message.answer("Введите группу которую вы представляете (Например ПИ-2401):")


@dp.message(Command("back"), GameState.task_reply)
@dp.message(F.text.casefold() == "back", GameState.task_reply)
async def go_back_to_selection(message: Message, state: FSMContext):
    await state.set_state(GameState.task_selection)

    await message.answer("Возвращение к выбору вопроса...")
    await display_tasks(message, state)


async def premature_end_command(message: Message, state: FSMContext):
    player_data: PlayerData = (await state.get_data()).get("player_data", None)

    if player_data.name == "":
        await message.answer("Нельзя закончить игру")

    for i, task in enumerate(tasks):
        if i in player_data.tasks:
            continue
        player_data.tasks[i] = 0

    await state.update_data(player_data=player_data)
    await process_end_game(message, state)


@dp.message(GameState.name_collection)
async def collect_name_and_start_game(message: Message, state: FSMContext) -> None:
    id, name = message.chat.id, message.text

    if not name:
        await message.answer("Введите название группы!")
        return

    if name in groups_that_started:
        await message.answer("Группа с таким именем уже начала игру.")
        return

    handle = message.from_user.username if message.from_user is not None else ""
    handle = handle if handle is not None else ""
    player_data = PlayerData(name, handle, id)
    player_data.fixate_start_time()
    current_players.add(id)
    groups_that_started.append(name)
    await state.update_data(player_data=player_data)
    logging.info(f"Пользователь {player_data} начал игру.")

    await display_tasks(message, state)


async def display_tasks(message: Message, state: FSMContext) -> None:
    player_data: PlayerData = (await state.get_data()).get("player_data", None)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=task, callback_data=f"{i}")]
            for i, task in filter(
                lambda x: x[0] not in player_data.tasks, enumerate(tasks)
            )
        ]
    )

    if len(keyboard.inline_keyboard) == 0:
        await process_end_game(message, state)
        return

    await message.answer(
        text="Выберите название уровня, на котором вы находитесь:",
        reply_markup=keyboard,
    )
    await state.set_state(GameState.task_selection)


@dp.callback_query(GameState.task_selection)
async def task_selection_handler(query: CallbackQuery, state: FSMContext) -> None:
    player_data: PlayerData = (await state.get_data()).get("player_data", None)

    selection = query.data
    if selection is None or not selection.isdigit():
        return

    cur_task = int(selection)
    player_data.cur_task = cur_task
    await state.update_data(player_data=player_data)
    await state.set_state(GameState.task_reply)

    await query.message.answer(  # type: ignore
        f"Введите ответ на задание '{tasks[cur_task]}'\nЛибо нажмите /back чтобы вернутся к выбору вопроса:"
    )


@dp.message(GameState.task_reply)
async def process_task_reply(message: Message, state: FSMContext) -> None:
    player_data: PlayerData = (await state.get_data()).get("player_data", None)

    if player_data.cur_task in player_data.tasks:
        await message.answer(f"{html.bold("ОШИБКА")} Вы уже ответили на это задание!")
        await display_tasks(message, state)
        return

    if not message.text:
        await message.answer(
            f"Введите ответ на задание '{tasks[player_data.cur_task]}':"
        )
        return

    points = get_points_from_answer(message.text)
    player_data.tasks[player_data.cur_task] = points
    await state.update_data(player_data=player_data)

    await state.set_state(GameState.task_selection)

    await message.answer("Ответ принят.")

    await display_tasks(message, state)


async def process_end_game(message: Message, state: FSMContext) -> None:
    player_data: PlayerData = (await state.get_data()).get("player_data", None)
    player_data.fixate_end_time()

    await message.answer_photo(FSInputFile("img/end.png"), texts.GAME_END)

    current_players.remove(player_data.id)
    await state.clear()

    result_writer.write(player_data)


async def times_up():
    from aiogram.fsm.storage.base import StorageKey

    current_players_cp = current_players.copy()
    for user_id in current_players_cp:
        message = await bot.send_message(user_id, "Время вышло!")

        key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        # get state by user_id
        state = FSMContext(storage=dp.storage, key=key)
        await premature_end_command(message, state)


async def main() -> None:
    await dp.start_polling(bot)
    print(f"Завершение игры. Подождите пока все результаты будут записаны!\n \
            Бот больше не будет отвечать на сообщения. Кол-во игроков к записи {len(current_players)}")
    await times_up()


if __name__ == "__main__":
    file = getenv("LOG_FILE")
    if file is None:
        logging.basicConfig(level=logging.INFO)
    else:
        with open(file, mode="w") as f:
            print(f"Запуск бота. Файл с логами: {os.path.realpath(f.name)}")
            logging.basicConfig(level=logging.INFO, stream=f)
    
    asyncio.run(main())
