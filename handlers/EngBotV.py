import asyncio
import random
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from data import EngBotDB
from keyboards import reply, inline
from handlers.EngBotCommands import bonus
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states import CommandsFSM, vFSM
import csv
from utils import get_translations

router = Router()


async def csv_get_word(diff):
    words_list = []
    with open("data/oxford-5000.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            match diff:
                case "easy":
                    if row[2] in ("a1", "a2"):
                        words_list.append(row)
                case "medium":
                    if row[2] in ("b1", "b2"):
                        words_list.append(row)
                case "hard":
                    if row[2] == "c1":
                        words_list.append(row)
                case "mixed":
                    words_list.append(row)

    return words_list


@router.message(
    StateFilter(None, CommandsFSM.practice),
    F.text.lower().in_(["vocabulary", "/vocabulary"]),
)
async def voc_diff(message: Message, state: FSMContext):
    await message.answer("Let's get started")  # , reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    kb = await message.answer(
        "First, choose the difficulty🤔", reply_markup=inline.diff_kb
    )
    await state.update_data(voc_diff=kb)
    await state.update_data(lang=await EngBotDB.DB_select("language", message.from_user.id))


@router.callback_query(F.data.in_(["easy", "medium", "hard", "mixed"]))
async def voc_diff_cb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    call_d = callback.data
    user_data = await state.get_data()

    await bot.edit_message_reply_markup(
        chat_id=user_data["voc_diff"].chat.id,
        message_id=user_data["voc_diff"].message_id,
        reply_markup=None,
    )
    await asyncio.sleep(0.2)
    await callback.message.answer(
        "Great, now translate the words📝", reply_markup=reply.cancel_kb
    )
    await state.set_state(vFSM.voc_diff)

    words_list = await csv_get_word(call_d)
    word_eng = random.choice(words_list)
    await state.update_data(words_list=words_list)
    await state.update_data(word_eng=word_eng)
    await callback.message.answer(word_eng[0].capitalize())


@router.message(vFSM.voc_diff, F.text)
async def voc(message: Message, state: FSMContext):

    msg = message.text.lower()

    if msg == "❌":
        sc = await EngBotDB.DB_select("score", message.from_user.id)
        await message.answer(f"Your score: <b>{sc}</b>")
        await message.answer(
            "Successfully stopped, come back soon🤗", reply_markup=reply.practice_kb
        )
        await state.set_state(CommandsFSM.practice)
    else:
        user_data = await state.get_data()
        win_streak = user_data.get("win_streak_v", 0)
        word_eng = user_data["word_eng"]
        tr_flag = await EngBotDB.DB_select("tr_flag", message.from_user.id)
        lang = user_data["lang"]

        if word_eng[2] in ("a1", "a2"):
            ball = 1
        elif word_eng[2] in ("b1", "b2"):
            ball = 2
        elif word_eng[2] == "c1":
            ball = 3

        translate = await get_translations(word_eng[0], lang)

        if msg in translate:
            await message.answer("Correct✅")

            if win_streak + 1 == 5:
                b = await bonus(message.from_user.id, message.bot, vFSM.voc_diff, state)
                await EngBotDB.DB_score(message.from_user.id, ball + b)
                await state.update_data(win_streak_v=0)
            else:
                await state.update_data(win_streak_v=win_streak + 1)
                await EngBotDB.DB_score(message.from_user.id, ball)
        else:
            if tr_flag == "1":
                result = f" The correct answer is <b>{translate[0]}</b>"
            else:
                result = ""
            await message.answer("Incorrect❌" + result)
            await state.update_data(win_streak_v=0)
            await EngBotDB.DB_score(message.from_user.id, -ball)

        word_eng_new = random.choice(user_data["words_list"])
        await message.answer(word_eng_new[0].capitalize())
        await state.update_data(word_eng=word_eng_new)
