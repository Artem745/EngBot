import random
from aiogram import F, Router
from aiogram.types import Message
from data import EngBotDB
from keyboards import reply
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from handlers.EngBotWords import word_list
from apscheduler.jobstores.base import JobLookupError
from states import TheoryFSM, CommandsFSM
from utils import word_list, scheduler, parse_dict

router = Router()


@router.message(
    StateFilter(None, CommandsFSM.theory), F.text.lower() == "learn new word"
)
async def new_words(message: Message):
    word = random.choice(word_list)[0]
    await message.answer(await parse_dict(word))


async def schedule_word(freq, message):
    match freq:
        case "every 30 minutes":
            scheduler.add_job(
                new_words,
                "interval",
                minutes=30,
                id=str(message.from_user.id),
                args=(message,),
            )
        case "every 1 hour":
            scheduler.add_job(
                new_words,
                "interval",
                hours=1,
                id=str(message.from_user.id),
                args=(message,),
            )
        case "every 3 hours":
            scheduler.add_job(
                new_words,
                "interval",
                hours=3,
                id=str(message.from_user.id),
                args=(message,),
            )
        case "every day":
            scheduler.add_job(
                new_words,
                "interval",
                hours=24,
                id=str(message.from_user.id),
                args=(message,),
            )

    if not scheduler.running:
        scheduler.start()


@router.message(
    StateFilter(None, CommandsFSM.theory), F.text.lower() == "on/off auto word sending"
)
async def get_words(message: Message, state: FSMContext):
    if await EngBotDB.DB_select("frequency", message.from_user.id):
        await EngBotDB.DB_insert("frequency", "", message.from_user.id)
        await message.answer("Now i won't send you new words")
        try:
            scheduler.remove_job(str(message.from_user.id))
        except JobLookupError:
            pass
    else:
        await state.set_state(TheoryFSM.freq)
        await message.answer(
            "How often would you like to receive each word?", reply_markup=reply.freq_kb
        )


@router.message(
    StateFilter(None, TheoryFSM.freq),
    F.text.lower().in_(
        ["every 30 minutes", "every 1 hour", "every 3 hours", "every day"]
    ),
)
async def set_freq(message: Message, state: FSMContext):
    await message.answer(
        f"Now i will send you new words {message.text.lower()}",
        reply_markup=reply.theory_kb,
    )
    await EngBotDB.DB_insert("frequency", message.text.lower(), message.from_user.id)
    await schedule_word(message.text.lower(), message)
    await state.set_state(CommandsFSM.theory)
