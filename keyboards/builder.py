from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def quiz_kbf(quest):
    builder = ReplyKeyboardBuilder()
    for i in quest:
        builder.add(KeyboardButton(text=i))
    builder.add(KeyboardButton(text="❌"))
    builder.adjust(2)
    return builder