from aiogram.fsm.state import StatesGroup, State


class CommandsFSM(StatesGroup):
    restore_data = State()
    practice = State()
    theory = State()
    other = State()
    practice_settings = State()
    theory_settings = State()
    mot = State()
    bonus = State()
    lang = State()


class vFSM(StatesGroup):
    voc_diff = State()
    word_eng = State()
    win_streak_v = State()
    words_list = State()
    lang = State()


class qFSM(StatesGroup):
    quiz = State()
    win_streak_q = State()


class WordsFSM(StatesGroup):
    wordsg = State()
    wordsg_bot = State()
    wordsg_human_search = State()
    wordsg_human = State()
    used_words = State()


class TheoryFSM(StatesGroup):
    freq = State()
