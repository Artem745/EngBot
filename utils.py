from apscheduler.schedulers.asyncio import AsyncIOScheduler
import csv
from aiogram.fsm.storage.memory import MemoryStorage
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import logging

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


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_translations(word, language):
    url = f"https://context.reverso.net/translation/english-{language}/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession() as session:  # Create session per request
            async with session.get(url, headers=headers, timeout=timeout) as response:
                logger.info(f"Requesting {url}, status: {response.status}")
                if response.status == 429:
                    logger.warning("Rate limit hit, retrying after 5 seconds")
                    await asyncio.sleep(5)
                    return await get_translations(word, language)  # Retry
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}, status: {response.status}")
                    return []  # Return empty list on failure

                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                translation_elements = soup.find_all("span", class_="display-term")

                translations = [
                    element.get_text().strip()
                    for element in translation_elements
                    if element.get_text().strip()
                ]

                if not translations:
                    logger.warning(f"No translations found for '{word}' in {language}")
                else:
                    logger.info(f"Found translations for '{word}': {translations}")
                return translations if translations else []

    except aiohttp.ClientError as e:
        logger.error(f"Network error for '{word}' in {language}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error for '{word}' in {language}: {str(e)}")
        return []


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
        if resp.status == 200:
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
