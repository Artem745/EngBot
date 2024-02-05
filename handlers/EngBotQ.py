import random
from aiogram import F, Router
from aiogram.types import Message
from data import EngBotDB
from keyboards import reply, builder
from handlers.EngBotCommands import bonus
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from data.materials import quiz_dict

router = Router()


class qFSM(StatesGroup):
    quiz = State()
    win_streak_q = State()


@router.message(StateFilter(None), F.text.lower().in_(["quiz","/quiz"]))
async def quiz1(message: Message, state: FSMContext):
    await message.answer('Get ready. You need to choose the correct answer out of 4 possible ones📃')
    quiz_quest = random.choice(list(quiz_dict.keys()))
    builderr = await builder.quiz_kbf(quiz_dict[quiz_quest][:-1])
    await message.answer(quiz_quest, reply_markup=builderr.as_markup(resize_keyboard=True))
    await state.update_data(quiz=quiz_quest)
    await state.set_state(qFSM.quiz)


@router.message(qFSM.quiz, F.text)
async def quiz(message: Message, state: FSMContext):

    msg = message.text.lower()
    print(msg)

    if msg == "❌":
        sc = await EngBotDB.DB_select("score", message.from_user.id)
        await message.answer(f'Your score: <b>{sc}</b>')
        await message.answer('Successfully stopped, come back soon🤗', reply_markup=reply.main_kb)
        await state.set_state(state=None)

    else:
        user_data = await state.get_data()
        quiz_quest = user_data["quiz"]
        try:
            ws = user_data["win_streak_q"]
        except KeyError:
            await state.update_data(win_streak_q=0)
            ws = 0
        tr_flag = await EngBotDB.DB_select("tr_flag", message.from_user.id)

        quiz_answer = quiz_dict[quiz_quest][-1]
        print(quiz_answer)

        if msg == quiz_answer:
            await message.answer("Correct✅")
            if ws + 1 == 5:
                b = await bonus(message.from_user.id, message.bot)
                await EngBotDB.DB_score(message.from_user.id, 2 + b)
                await state.update_data(win_streak_q=0)
            else:
                await EngBotDB.DB_score(message.from_user.id, 2)
                ws += 1
                await state.update_data(win_streak_q=ws)

        else:
            if tr_flag == "1":
                tr = f" The correct answer is <b>{quiz_answer}</b>"
            else: tr = ""
            await message.answer("Incorrect❌" + tr)
            await state.update_data(win_streak_q=0)
            await EngBotDB.DB_score(message.from_user.id, -2)

        quiz_quest_new = random.choice(list(quiz_dict.keys()))
        builderr = await builder.quiz_kbf(quiz_dict[quiz_quest_new][:-1])
        await message.answer(quiz_quest_new, reply_markup=builderr.as_markup(resize_keyboard=True))
        await state.update_data(quiz=quiz_quest_new)
