from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Vocabulary"), KeyboardButton(text="Quiz")],
        [KeyboardButton(text="Info"), KeyboardButton(text="Leaderboard")],
        [KeyboardButton(text="Other")]
    ],
    resize_keyboard=True,
    selective=True)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌")]
    ],
    resize_keyboard=True,
    selective=True)

other_kb = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text="On/off answers"), KeyboardButton(text="Change language to translate")],
    [KeyboardButton(text="Word Chain Game"), KeyboardButton(text="Motivation")],
    [KeyboardButton(text="Back")]
    ],
    resize_keyboard=True,
    selective=True)
