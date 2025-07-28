import random
from aiogram import F, Bot, Router
from aiogram.types import Message
from keyboards import reply
from aiogram.fsm.context import FSMContext
from states import CommandsFSM, WordsFSM
from spellchecker import SpellChecker
from aiogram.filters import StateFilter
from data.EngBotDB import DB_score
from utils import word_list, scheduler, storage
from aiogram.fsm.storage.base import StorageKey


router = Router()

spell = SpellChecker()


async def word_check(w):
    return len(w) > 1 and spell[w]


players_search = []

players_games = {}


@router.message(
    StateFilter(None, CommandsFSM.practice), F.text.lower() == "word chain game"
)
async def words(message: Message, state: FSMContext):
    await message.answer("Who would you play against", reply_markup=reply.words_game_kb)
    await state.set_state(WordsFSM.wordsg)


@router.message(StateFilter(WordsFSM.wordsg), F.text)
async def words_game(message: Message, state: FSMContext, bot: Bot):
    if message.text.lower() == "play against bot":
        await state.set_state(WordsFSM.wordsg_bot)
        await message.answer(
            "Word Chain - is a game in which you have to write a word that starts with the last letter of "
            "your opponent's word🔄"
        )
        await message.answer("I'll start")
        word = random.choice(word_list)[0]
        await state.update_data(wordsg_bot=word)
        await message.answer(word.capitalize(), reply_markup=reply.giveup_kb)
        await state.update_data(used_words=[word])

    if message.text.lower() == "play against human":
        await message.answer(
            "Word Chain - is a game in which you have to write a word that starts with the last letter of "
            "your opponent's word🔄"
        )
        await message.answer("Searching for opponent...", reply_markup=reply.cancel_kb)
        players_search.append(message.from_user.id)
        await state.set_state(WordsFSM.wordsg_human_search)
        scheduler.add_job(
            words_human_search,
            "interval",
            seconds=3,
            id=f"search{message.from_user.id}",
            args=(bot,),
        )
        if not scheduler.running:
            scheduler.start()

    if message.text.lower() == "back":
        await message.answer("Returned👌", reply_markup=reply.practice_kb)
        await state.set_state(CommandsFSM.practice)


@router.message(WordsFSM.wordsg_bot, F.text)
async def words_game_bot(message: Message, state: FSMContext):
    user_data = await state.get_data()
    used_words = user_data["used_words"]
    word_game = user_data["wordsg_bot"]
    msg = message.text.lower()

    if msg == "give up":
        await message.answer(
            "Good game, come back soon🤗", reply_markup=reply.practice_kb
        )
        await state.set_state(CommandsFSM.practice)

    elif msg in used_words:
        await message.answer("Hey, this word has already been. Any other options?")
    elif word_game[-1] != msg[0]:
        await message.answer(
            "The first letter of your word is not the same as the last letter of mine. "
            "Any other options?"
        )
    elif not await word_check(msg.lower()):
        await message.answer("Sorry, I don't know that word. Any other options?")
    else:
        used_words.append(msg)

        async def new():
            attempt = 0
            while attempt < 50000:
                word_new = random.choice(word_list)[0]
                if word_new[0] == msg[-1] and word_new not in used_words:
                    await message.answer(word_new.capitalize())
                    await state.update_data(wordsg_bot=word_new)
                    used_words.append(word_new)
                    await state.update_data(used_words=used_words)
                    return
                else:
                    attempt += 1
            await message.answer(
                "Wow, you have a great vocabulary, I don't know what to say to you"
            )
            await message.answer(
                "Your reward is 50 points, you deserve it😎",
                reply_markup=reply.practice_kb,
            )
            await DB_score(message.from_user.id, 50)
            await state.set_state(CommandsFSM.practice)

        await new()


async def words_human_search(bot):
    global players_search
    if len(players_search) >= 2:
        players = players_search[:2]
        players_search = players_search[2:]
        player_who_starts_id = random.choice(players)
        player_who_starts_name = await bot.get_chat(player_who_starts_id)
        for player in players:
            scheduler.remove_job(f"search{player}")
            opponent_id = [x for x in players if x != player][0]
            opponent_name = await bot.get_chat(opponent_id)
            await bot.send_message(
                chat_id=player,
                text=f"Your opponent is <b>{opponent_name.first_name}</b>",
                reply_markup=reply.giveup_kb,
            )
            await bot.send_message(
                chat_id=player, text="The game will be started by..."
            )
            await bot.send_message(
                chat_id=player, text=f"<b>{player_who_starts_name.first_name}</b>"
            )

        await bot.send_message(chat_id=player_who_starts_id, text="Enter a word")
        players_games[tuple(players)] = [player_who_starts_id]


@router.message(StateFilter(WordsFSM.wordsg_human_search), F.text)
async def words_game_human(message: Message, state: FSMContext, bot: Bot):
    msg = message.text.lower()
    player_id = message.from_user.id
    if players_games:
        for players_ids, value in players_games.items():
            if player_id in players_ids:
                second_player_id = [x for x in players_ids if x != player_id][0]
                current_player = value[0]
                used_words = value[1:]
                if msg == "give up":
                    await message.answer("Game stopped")
                    await message.answer(
                        "Since you gave up, you lose 20 points😞",
                        reply_markup=reply.words_game_kb,
                    )
                    await DB_score(player_id, -20)

                    await bot.send_message(
                        chat_id=second_player_id, text="Your opponent has given up"
                    )
                    await bot.send_message(
                        chat_id=second_player_id,
                        text="You get 20 points. Good job☺️",
                        reply_markup=reply.words_game_kb,
                    )
                    await DB_score(second_player_id, 20)

                    await state.set_state(WordsFSM.wordsg)

                    new_user_storage_key = StorageKey(
                        bot.id, second_player_id, second_player_id
                    )
                    new_user_context = FSMContext(
                        storage=storage, key=new_user_storage_key
                    )
                    await new_user_context.set_state(WordsFSM.wordsg)

                    players_games.pop(players_ids)
                    return

                if player_id == current_player:
                    if not await word_check(msg):
                        await message.answer(
                            "Sorry, I don't know that word. Any other options?"
                        )
                        return
                    elif used_words:
                        if msg in used_words:
                            await message.answer(
                                "Hey, this word has already been. Any other options?"
                            )
                            return
                        elif used_words[-1][-1] != msg[0]:
                            await message.answer(
                                "The first letter of your word is not the same as the last letter of your opponent. "
                                "Any other options?"
                            )
                            return
                    await message.answer("Waiting for opponent")
                    opponent_name = await bot.get_chat(player_id)
                    await bot.send_message(
                        chat_id=second_player_id,
                        text=f"<b>{opponent_name.first_name}</b> said <b>{msg}</b>",
                    )
                    await bot.send_message(chat_id=second_player_id, text="Your turn")
                    players_games[players_ids][0] = second_player_id
                    players_games[players_ids].append(msg)

    if msg == "❌":
        players_search.remove(message.from_user.id)
        await message.answer("Search canceled", reply_markup=reply.words_game_kb)
        await state.set_state(WordsFSM.wordsg)
        scheduler.remove_job(f"search{message.from_user.id}")
