from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Vocabulary"), KeyboardButton(text="Quiz")],
        [KeyboardButton(text="Info"), KeyboardButton(text="Leaderboard")],
        [KeyboardButton(text="Other")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose a category",
    selective=True)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True)

other_kb = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text="On/off answers"), KeyboardButton(text="Motivation")],
    [KeyboardButton(text="Word Chain Game")],
    [KeyboardButton(text="Back")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True)