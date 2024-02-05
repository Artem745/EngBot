import asyncio
import random
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from data import EngBotDB
from keyboards import reply

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()


class CommandsFSM(StatesGroup):
    other = State()
    mot = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    st = await state.get_state()
    if st != CommandsFSM.mot:
        await message.answer(f"Welcome, <b>{message.from_user.first_name}</b>", reply_markup=reply.main_kb)
        await EngBotDB.DB_add(message.from_user.id, message.from_user.username, message.from_user.first_name,
                              message.from_user.last_name)
        await state.set_state(None)


@router.message(F.text.lower() == "info")
async def info(message: Message):
    await message.answer("Hello! This is an English learning bot🤖")
    await asyncio.sleep(0.3)
    await message.answer("You can improve your English skills here. Just click on \"/Vocabulary\" or \"/Quiz\". For each correct and incorrect answer I\'ll add or deduct points, depending on their difficulty. So think carefully🧠")


@router.message(F.text.lower() == "leaderboard")
async def lb(message: Message):
    await message.answer(await EngBotDB.DB_leaderboard())


@router.message(StateFilter(None), F.text.lower() == "other")
async def other(message: Message, state: FSMContext):
    await message.answer("Let's see👀", reply_markup=reply.other_kb)
    await state.set_state(CommandsFSM.other)


@router.message(CommandsFSM.other, F.text.lower() == "back")
async def other(message: Message, state: FSMContext):
    await message.answer("Returned👌", reply_markup=reply.main_kb)
    await state.set_state(None)


@router.message(CommandsFSM.other, F.text.lower() == "motivation")
async def other(message: Message, state: FSMContext):
    await state.set_state(CommandsFSM.mot)
    from data.materials import motivation

    k, v = random.choice(list(motivation.items()))

    for i in v:
        el = i[:-3]
        time = i[-3:]
        await message.answer(el)
        await asyncio.sleep(float(time))
    if len(k) > 1:
        author = k[:-1]
        await message.answer(f"<b>{author}</b>")
    await state.set_state(CommandsFSM.other)


@router.message(F.text.lower() == "on/off answers")
async def tr(message: Message):
    if await EngBotDB.DB_select("tr_flag", message.from_user.id) == "0":
        await message.answer("Now I <b>will</b> show you the correct answer if you make a mistake")
        await EngBotDB.DB_insert("tr_flag", "1", message.from_user.id)
    else:
        await message.answer("Now I <b>won't</b> show you the correct answer if you make a mistake")
        await EngBotDB.DB_insert("tr_flag", "0", message.from_user.id)


@router.message(F.text.lower() == "word chain game")
async def words(message: Message):
    from data.materials import voc_dict
    if await EngBotDB.DB_select("words_flag", message.from_user.id) == "0":
        await EngBotDB.DB_insert("words_flag", "1", message.from_user.id)
        word = random.choice(list(voc_dict["mixed"].keys()))
        await message.answer(word)
        await EngBotDB.DB_insert("word_eng", word, message.from_user.id)


async def bonus(chat_id, bot):
    await bot.send_message(chat_id, "Good job! You answered correctly <b>5</b> times in a row, so here's your <b>bonus</b>")
    result: Message = await bot.send_dice(chat_id=chat_id, emoji=random.choice(["🎲","🎯","🏀","⚽","🎳"]))
    point = result.dice.value
    await asyncio.sleep(4)
    if point == 1:
        await bot.send_message(chat_id, f"+{str(result.dice.value)} point")
    else:
        await bot.send_message(chat_id, f"+{str(result.dice.value)} points")
    await asyncio.sleep(1)
    return point


