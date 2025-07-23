from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def quiz_kbf(quest):
    builder = ReplyKeyboardBuilder()
    for i in quest:
        builder.add(KeyboardButton(text=i))
    builder.add(KeyboardButton(text="❌"))
    builder.adjust(2)
    return builder


async def langs_kb():
    languages = [
        "Arabic",
        "Chinese",
        "Dutch",
        "French",
        "German",
        "Hebrew",
        "Italian",
        "Japanese",
        "Korean",
        "Polish",
        "Portuguese",
        "Romanian",
        "Russian",
        "Spanish",
        "Swedish",
        "Turkish",
        "Ukrainian",
    ]

    builder = ReplyKeyboardBuilder()
    for l in languages:
        builder.add(KeyboardButton(text=l))
    builder.adjust(3)
    return builder
