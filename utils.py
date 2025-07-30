from apscheduler.schedulers.asyncio import AsyncIOScheduler
import csv
from aiogram.fsm.storage.memory import MemoryStorage
from bs4 import BeautifulSoup
import aiohttp
from deep_translator import GoogleTranslator

storage = MemoryStorage()

scheduler = AsyncIOScheduler()


async def init_session():
    global session
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, ttl_dns_cache=300))


async def close_session():
    global session
    if session:
        await session.close()


with open("data/oxford-5000.csv", "r") as file:
    reader = csv.reader(file)
    word_list = list(reader)


async def get_translations(word, language):
    url = f"https://glosbe.com/en/{language}/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")

            translation_elements = soup.find_all("h3", class_="align-top inline translation__item__pharse leading-10 text-primary-700 break-words font-medium text-base cursor-pointer")

            translations = [
                element.get_text().strip()
                for element in translation_elements
                if element.get_text().strip()
            ]
            if not translations:
                fallback = GoogleTranslator(source='en', target=language).translate(word)
                return [fallback]
            return translations


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
    ) as response:
        if response.status == 200:
            text = await response.text()
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
