from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Practice")],
        [KeyboardButton(text="Theory")],
        [KeyboardButton(text="Other")],
    ],
    resize_keyboard=True,
    selective=True,
)

practice_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Vocabulary"), KeyboardButton(text="Quiz")],
        [KeyboardButton(text="Word Chain Game"), KeyboardButton(text="Leaderboard")],
        [KeyboardButton(text="Settings"), KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
    selective=True,
)

theory_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Learn new word"),
            KeyboardButton(text="On/off auto word sending"),
        ],
        # [KeyboardButton(text="Settings")],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
    selective=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌")]], resize_keyboard=True, selective=True
)

giveup_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Give up")]], resize_keyboard=True, selective=True
)

practice_settings_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="On/off answers"),
            KeyboardButton(text="Change language to translate"),
        ],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
    selective=True,
)

# theory_settings_kb = ReplyKeyboardMarkup(
#     keyboard=[
#     [KeyboardButton(text="Show translation"), KeyboardButton(text="Change frequency")],
#     [KeyboardButton(text="Back")]
#     ],
#     resize_keyboard=True,
#     selective=True)

other_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Motivation"), KeyboardButton(text="Info")],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
    selective=True,
)

freq_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Every 30 minutes"), KeyboardButton(text="Every 1 hour")],
        [KeyboardButton(text="Every 3 hours"), KeyboardButton(text="Every day")],
    ],
    resize_keyboard=True,
    selective=True,
)

words_game_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Play against bot"),
            KeyboardButton(text="Play against human"),
        ],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
    selective=True,
)
