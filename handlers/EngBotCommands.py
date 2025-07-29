import asyncio
import random
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from data import EngBotDB
from keyboards import reply, builder
from aiogram.fsm.context import FSMContext
from handlers.EngBotTheory import schedule_word
from states import CommandsFSM

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    st = await state.get_state()
    if st != CommandsFSM.mot and st != CommandsFSM.bonus:
        print(message.chat.id)
        await message.answer(
            f"Welcome, <b>{message.from_user.first_name}</b>",
            reply_markup=reply.main_kb,
        )
        await EngBotDB.DB_add(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

        send_word_freq = await EngBotDB.DB_select("frequency", message.from_user.id)
        if send_word_freq:
            await schedule_word(send_word_freq, message)

        await state.set_state(None)


@router.message(StateFilter(None), F.text.lower() == "other")
async def other(message: Message, state: FSMContext):
    await message.answer("Let's see👀", reply_markup=reply.other_kb)
    await state.set_state(CommandsFSM.other)


@router.message(StateFilter(None, CommandsFSM.other), F.text.lower() == "info")
async def info(message: Message):
    await message.answer("Hello! This is an English learning bot🤖")
    await asyncio.sleep(0.3)
    await message.answer(
        'You can improve your English skills here! Choose "Practice" to test your knowledge or "Theory" to learn something new. In Practice mode, you\'ll earn or lose points based on your answers\' correctness and difficulty'
    )
    await asyncio.sleep(0.3)
    await message.answer("Think carefully and enjoy learning!🧠")


@router.message(F.text.lower() == "leaderboard")
async def lb(message: Message):
    await message.answer(await EngBotDB.DB_leaderboard())


@router.message(CommandsFSM.other, F.text.lower() == "motivation")
async def motivation(message: Message, state: FSMContext):
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


@router.message(StateFilter(None), F.text.lower().in_(["practice", "/practice"]))
async def practice(message: Message, state: FSMContext):
    await message.answer("Lets's test your skills😏", reply_markup=reply.practice_kb)
    await state.set_state(CommandsFSM.practice)


@router.message(StateFilter(None), F.text.lower().in_(["theory", "/theory"]))
async def theory(message: Message, state: FSMContext):
    await message.answer("Lets's learn something new📚", reply_markup=reply.theory_kb)
    await state.set_state(CommandsFSM.theory)


@router.message(
    StateFilter(CommandsFSM.other, CommandsFSM.practice, CommandsFSM.theory),
    F.text.lower() == "back",
)
async def back(message: Message, state: FSMContext):
    await message.answer("Returned👌", reply_markup=reply.main_kb)
    await state.set_state(None)


@router.message(CommandsFSM.practice, F.text.lower() == "settings")
async def practice_settings(message: Message, state: FSMContext):
    await message.answer("Configuring⚙️", reply_markup=reply.practice_settings_kb)
    await state.set_state(CommandsFSM.practice_settings)


@router.message(CommandsFSM.practice_settings, F.text.lower() == "back")
async def back(message: Message, state: FSMContext):
    await message.answer("Returned👌", reply_markup=reply.practice_kb)
    await state.set_state(CommandsFSM.practice)


@router.message(CommandsFSM.practice_settings, F.text.lower() == "on/off answers")
async def tr(message: Message):
    if await EngBotDB.DB_select("tr_flag", message.from_user.id) == "0":
        await message.answer(
            "Now I <b>will</b> show you the correct answer if you make a mistake"
        )
        await EngBotDB.DB_insert("tr_flag", "1", message.from_user.id)
    else:
        await message.answer(
            "Now I <b>won't</b> show you the correct answer if you make a mistake"
        )
        await EngBotDB.DB_insert("tr_flag", "0", message.from_user.id)


@router.message(
    CommandsFSM.practice_settings, F.text.lower() == "change language to translate"
)
async def change_language(message: Message, state: FSMContext):
    kb = await builder.langs_kb()
    await message.answer(
        "Select language to translate in vocabulary game...",
        reply_markup=kb.as_markup(resize_keyboard=True),
    )
    await state.set_state(CommandsFSM.lang)


@router.message(
    CommandsFSM.lang,
    F.text.lower().in_(
        [
            "arabic",
            "chinese",
            "dutch",
            "french",
            "german",
            "hebrew",
            "italian",
            "japanese",
            "korean",
            "polish",
            "portuguese",
            "romanian",
            "russian",
            "spanish",
            "swedish",
            "turkish",
            "ukrainian",
        ]
    ),
)
async def change_language(message: Message, state: FSMContext):
    await EngBotDB.DB_insert(
        "language", message.text.lower(), message.from_user.id
    )
    await message.answer(
        f"Successfully selected {message.text.lower()}", reply_markup=reply.practice_settings_kb
    )
    await state.set_state(CommandsFSM.practice_settings)


async def bonus(chat_id, bot, vq, state):
    await state.set_state(CommandsFSM.bonus)
    await bot.send_message(
        chat_id,
        "Good job! You answered correctly <b>5</b> times in a row, so here's your <b>bonus</b>",
    )
    result: Message = await bot.send_dice(
        chat_id=chat_id, emoji=random.choice(["🎲", "🎯", "🏀", "⚽", "🎳"])
    )
    point = result.dice.value
    await asyncio.sleep(4)
    if point == 1:
        await bot.send_message(chat_id, f"+{str(result.dice.value)} point")
    else:
        await bot.send_message(chat_id, f"+{str(result.dice.value)} points")
    await asyncio.sleep(1)
    await state.set_state(vq)
    return point


# @router.message(CommandsFSM.theory, F.text.lower() == "settings")
# async def practice_settings(message: Message, state: FSMContext):
#     await message.answer("Configuring⚙️", reply_markup=reply.theory_settings_kb)
#     await state.set_state(CommandsFSM.theory_settings)

# @router.message(CommandsFSM.theory_settings, F.text.lower() == "back")
# async def back(message: Message, state: FSMContext):
#     await message.answer("Returned👌", reply_markup=reply.theory_kb)
#     await state.set_state(CommandsFSM.theory)
