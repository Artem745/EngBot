from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

diff_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy", callback_data="easy"),
            InlineKeyboardButton(text="Medium", callback_data="medium"),
            InlineKeyboardButton(text="Hard", callback_data="hard"),
        ],
        [InlineKeyboardButton(text="Mixed", callback_data="mixed")],
    ]
)

links_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Youtube",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            ),
            InlineKeyboardButton(text="Telegram", url="https://t.me/engFlue"),
        ]
    ]
)
