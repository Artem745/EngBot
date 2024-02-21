import asyncio
import random
from aiogram import F, Router
from aiogram.types import Message
from keyboards import reply
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from handlers.EngBotCommands import CommandsFSM
from spellchecker import SpellChecker

router = Router()


class WordsFSM(StatesGroup):
    wordsg = State()
    used_words = State()


with open("data/filtered_words.txt", "r") as file:
    word_list = file.readlines()


@router.message(CommandsFSM.other, F.text.lower() == "word chain game")
async def words(message: Message, state: FSMContext):
    await state.set_state(WordsFSM.wordsg)
    await message.answer("Word Chain - is a game in which you have to write a word that starts with the last letter of "
                         "your opponent's word🔄")
    await message.answer("I'll start")
    word = random.choice(word_list).strip()
    print(word)
    await state.update_data(wordsg=word)
    await message.answer(word.capitalize(), reply_markup=reply.cancel_kb)
    await state.update_data(used_words=[word])


@router.message(WordsFSM.wordsg, F.text)
async def words_game(message: Message, state: FSMContext):
    spell = SpellChecker()

    async def word_check(w):
        if w == spell.correction(w):
            print(w)
            return True
        else:
            return False

    user_data = await state.get_data()
    used_words = user_data["used_words"]
    word_game = user_data["wordsg"]
    print(used_words)
    msg = message.text.lower()
    if msg == "❌":
        await message.answer("Good game, come back soon🤗", reply_markup=reply.other_kb)
        await state.set_state(CommandsFSM.other)
    elif msg not in used_words and word_game[-1] == msg[0] and await word_check(msg.lower()):
        used_words.append(msg)

        async def new():
            attempt = 0
            while attempt < 8700:
                word_new = random.choice(word_list).strip()
                if word_new[0] == msg[-1] and word_new not in used_words:
                    await message.answer(word_new.capitalize())
                    await state.update_data(wordsg=word_new)
                    used_words.append(word_new)
                    await state.update_data(used_words=used_words)
                    return
                else:
                    attempt += 1
            await message.answer("Wow, you have a great vocabulary, I don't know what to say to you")
            await message.answer("Your reward is 50 points, you deserve it😎", reply_markup=reply.other_kb)
            await state.set_state(CommandsFSM.other)
        await new()

    else:
        if msg in used_words:
            await message.answer("Hey, this word has already been. Any other options?")
        elif word_game[-1] != msg[0]:
            await message.answer("The first letter of your word is not the same as the last letter of mine. "
                                 "Any other options?")
        else:
            await message.answer("Sorry, I don't know that word. Any other options?")
