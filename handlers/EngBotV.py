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
from data.materials import voc_dict

router = Router()


# print(len(voc_dict['easy']), len(voc_dict['medium']), len(voc_dict['hard']))


class vFSM(StatesGroup):
    voc_diff = State()
    word_eng = State()
    win_streak_v = State()


@router.message(StateFilter(None), F.text.lower().in_(["vocabulary","/vocabulary"]))
async def voc_diff(message: Message):
    global kb
    await message.answer("Let's get started")  #, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    kb = await message.answer("First, choose the difficulty🤔", reply_markup=inline.diff_kb)


@router.callback_query(F.data.in_(["easy", "medium", "hard", "mixed"]))
async def voc_diff_cb(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    call_d = callback.data
    await state.update_data(voc_diff=call_d)
    await bot.edit_message_reply_markup(chat_id=kb.chat.id, message_id=kb.message_id, reply_markup=None)
    await asyncio.sleep(0.3)
    await callback.message.answer("Great, now translate the words📝", reply_markup=reply.cancel_kb)
    await asyncio.sleep(0.2)
    await state.set_state(vFSM.voc_diff)
    word_eng = random.choice(list(voc_dict[call_d].keys()))
    await callback.message.answer(word_eng)
    await state.update_data(word_eng=word_eng)


@router.message(vFSM.voc_diff, F.text)
async def voc(message: Message, state: FSMContext):

    msg = message.text.lower()
    print(msg)

    if msg == "❌":
        sc = await EngBotDB.DB_select("score", message.from_user.id)
        await message.answer(f'Your score: <b>{sc}</b>')
        await message.answer('Successfully stopped, come back soon🤗', reply_markup=reply.main_kb)
        await state.set_state(state=None)
    else:
        user_data = await state.get_data()
        diff = user_data["voc_diff"]
        word_eng = user_data["word_eng"]
        try:
            ws = user_data["win_streak_v"]
        except KeyError:
            await state.update_data(win_streak_v=0)
            ws = 0
        tr_flag = await EngBotDB.DB_select("tr_flag", message.from_user.id)

        if diff == "easy":
            ball = 1
        elif diff == "medium":
            ball = 2
        elif diff == "hard":
            ball = 3
        elif diff == "mixed":
            if word_eng in voc_dict["easy"].keys():
                ball = 1
            elif word_eng in voc_dict["medium"].keys():
                ball = 2
            elif word_eng in voc_dict["hard"].keys():
                ball = 3

        translate = voc_dict[diff][word_eng]
        print(translate)

        if isinstance(translate, list):
            if msg in translate:
                await message.answer("Correct✅")
                await EngBotDB.DB_score(message.from_user.id, ball)

                if ws + 1 == 5:
                    b = await bonus(message.from_user.id, message.bot)
                    await EngBotDB.DB_score(message.from_user.id, ball + b)
                    await state.update_data(win_streak_v=0)
                else:
                    ws += 1
                    await state.update_data(win_streak_v=ws)
            else:
                if tr_flag == "1":
                    result = f" The correct answer is <b>{translate[0]}</b>"
                else: result = ""
                await message.answer("Incorrect❌" + result)
                await state.update_data(win_streak_v=0)
                await EngBotDB.DB_score(message.from_user.id, -ball)
        else:
            if msg == translate:
                await message.answer("Correct✅")
                await EngBotDB.DB_score(message.from_user.id, ball)

                if ws + 1 == 5:
                    b = await bonus(message.from_user.id, message.bot)
                    await EngBotDB.DB_score(message.from_user.id, ball + b)
                    await state.update_data(win_streak_v=0)
                else:
                    ws += 1
                    await state.update_data(win_streak_v=ws)
            else:
                if tr_flag == "1":
                    result = f" The correct answer is <b>{translate}</b>"
                else: result = ""
                await message.answer("Incorrect❌" + result)
                await state.update_data(win_streak_v=0)
                await EngBotDB.DB_score(message.from_user.id, -ball)

        word_eng_new = random.choice(list(voc_dict[diff].keys()))
        print(word_eng_new)
        await message.answer(word_eng_new)
        await state.update_data(word_eng=word_eng_new)
