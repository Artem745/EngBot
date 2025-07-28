import random
from aiogram import Bot, F, Router
from aiogram.types import Message
import aiohttp
from data import EngBotDB
from keyboards import reply
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from reverso_context_api import Client
from handlers.EngBotWords import word_list
from bs4 import BeautifulSoup
from apscheduler.jobstores.base import JobLookupError
from states import TheoryFSM, CommandsFSM
from utils import word_list, scheduler
from aiohttp import ClientSession, TCPConnector

router = Router()


async def init_session():
    global session
    session = ClientSession(connector=TCPConnector(ssl=False, ttl_dns_cache=300))


async def close_session():
    global session
    if session:
        await session.close()


async def parse_dict(word):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    async with session.get(
        f"https://dictionary.cambridge.org/dictionary/english/{word}", headers=headers
    ) as resp:
        text = await resp.text()
        soup = BeautifulSoup(text, "lxml")
        page = soup.find("div", class_="pr dictionary")
        blocks = page.find_all("div", class_="pr entry-body__el")
        result = [f"🌟 <b><code>{word.upper()}</code></b> 🌟\n"]
        for block in blocks:
            result.append("\n")

            p = block.find("span", class_="pos dpos")
            if p:
                result.append(f"💬 Part of speech: <b>{p.text}</b>\n")
            tr = block.find_all("span", class_="pron dpron")
            if tr:
                result.append(f"🇬🇧 <b>{tr[0].text}</b>  🇺🇸 <b>{tr[1].text}</b>\n")
            lvl = block.select("span.epp-xref.dxref")
            if lvl:
                result.append(f"💢 Level: <b>{lvl[0].text}</b>\n")
            d = block.find("div", class_="def ddef_d db")
            if d:
                result.append(f"📋 Definition: {d.text}\n")
            examples_block = block.find("div", class_="def-body ddef_b")
            if examples_block:
                examples = examples_block.find_all("span", class_="eg deg")
                if examples:
                    result.append("🤔 Examples:\n")
                    n = 0
                    for example in examples:
                        result.append(f"- {example.text}\n")
                        n += 1
                        if n == 4:
                            break
        return "".join(result)


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
                seconds=30,
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
