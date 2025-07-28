from apscheduler.schedulers.asyncio import AsyncIOScheduler
import csv
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()

scheduler = AsyncIOScheduler()

with open("data/oxford-5000.csv", "r") as file:
    reader = csv.reader(file)
    word_list = list(reader)