import asyncio
import random
from aiogram import Bot, types, F, Router
from aiogram.types import Message
from data import EngBotDB
from keyboards import reply, inline
from handlers.EngBotCommands import bonus
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import csv
from reverso_context_api import Client


router = Router()


class vFSM(StatesGroup):
    voc_diff = State()
    word_eng = State()
    win_streak_v = State()
    words_list = State()
    lang = State()


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




async def translate_text(word, lang):
    result = list(lang.get_translations(word))
    if len(result) > 10:
        return result[:10]
    else:
        return result


@router.message(StateFilter(None), F.text.lower().in_(["vocabulary", "/vocabulary"]))
async def voc_diff(message: Message, state: FSMContext):
    global kb #???
    await message.answer("Let's get started")  # , reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    kb = await message.answer(
        "First, choose the difficulty🤔", reply_markup=inline.diff_kb
    )
    
    l = await EngBotDB.DB_select("language", message.from_user.id)
    client = Client("en", l)
    await state.update_data(lang=client)


@router.callback_query(F.data.in_(["easy", "medium", "hard", "mixed"]))
async def voc_diff_cb(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    call_d = callback.data
    await bot.edit_message_reply_markup(
        chat_id=kb.chat.id, message_id=kb.message_id, reply_markup=None
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
    print(msg)

    if msg == "❌":
        sc = await EngBotDB.DB_select("score", message.from_user.id)
        await message.answer(f"Your score: <b>{sc}</b>")
        await message.answer(
            "Successfully stopped, come back soon🤗", reply_markup=reply.main_kb
        )
        await state.set_state(state=None)
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

        translate = await translate_text(word_eng[0], lang)
        print(translate)
        print(" ")

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
        print(word_eng_new)
        await message.answer(word_eng_new[0].capitalize())
        await state.update_data(word_eng=word_eng_new)
