import asyncio
import aiosqlite


async def DB():
    async with aiosqlite.connect('EngBotDb.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                score INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS variables (
                        user_id TEXT PRIMARY KEY NOT NULL UNIQUE,
                        other_flag TEXT,
                        voc_flag TEXT,
                        tr_flag TEXT,
                        call_d TEXT, 
                        word_eng TEXT,
                        quiz_flag TEXT,
                        quiz_quest TEXT,
                        win_streak INTEGER,
                        words_flag TEXT)''')
        await db.commit()


async def DB_add(user_id, username, first_name, last_name, score=0, other_flag="0", voc_flag="0", tr_flag="0", word_eng=None, quiz_flag="0", quiz_quest=None, win_streak=0, words_flag="0"):
    async with aiosqlite.connect('data/EngBotDb.db') as db:
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?',(user_id,))
        if not await cursor.fetchone():
            await db.execute('INSERT INTO users (user_id, username, first_name, last_name, score) VALUES(?,?,?,?,?)', (user_id, username, first_name, last_name, score))
            await db.execute('INSERT INTO variables (user_id, other_flag, voc_flag, tr_flag, word_eng, quiz_flag, quiz_quest, win_streak, words_flag) VALUES(?,?,?,?,?,?,?,?,?)',(user_id, other_flag, voc_flag, tr_flag, word_eng, quiz_flag, quiz_quest, win_streak, words_flag))
        else:
            await db.execute('UPDATE variables SET other_flag = "0", voc_flag = "0", call_d = NULL, word_eng = NULL, quiz_flag="0", quiz_quest=NULL, win_streak="0", words_flag="0" WHERE user_id = ?',(user_id,))
            print('yge e')
        await db.commit()


async def DB_score(user_id, score):
    async with aiosqlite.connect('data/EngBotDb.db') as db:
        cursor = await db.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
        old_score = await cursor.fetchone()
        new_score = old_score[0] + score
        if new_score < 0:
            await db.execute('UPDATE users SET score = 0 WHERE user_id = ?', (user_id,))
        else:
            await db.execute('UPDATE users SET score = ? WHERE user_id = ?', (new_score, user_id))
        await db.commit()


async def DB_get_score(user_id):
    async with aiosqlite.connect('data/EngBotDb.db') as db:
        cursor = await db.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
        score = await cursor.fetchone()
        return score[0]


async def DB_leaderboard():
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        cursor = await db.execute('SELECT username, first_name, last_name, score FROM users ORDER BY score DESC')
        board = await cursor.fetchall()
        result = ''
        smiles = ["🥇","🥈","🥉"]
        for index, user in enumerate(board):
            if not user[0] and not user[2]:
                result += f"#{index + 1} {user[1]}. Score: {user[3]}"
            elif not user[2]:
                result += f"#{index + 1} {user[1]} @{user[0]}. Score: {user[3]}"
            elif not user[0]:
                result += f"#{index + 1} {user[1]}. Score: {user[3]}\n\n"
            else: result += f"#{index+1} {user[1]} {user[2]} @{user[0]}. Score: {user[3]}"
            if len(smiles) > index:
                result += f"{smiles[index]}\n\n"
            else: result += "\n\n"
        return result


async def DB_var_select(flag, user_id):
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        a = await db.execute(f'SELECT {flag} FROM variables WHERE user_id = ?',(user_id,))
        a = await a.fetchone()
        return a[0]


async def DB_var_insert(flag, number, user_id):
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        await db.execute(f'UPDATE variables SET {flag} = ? WHERE user_id = ?',(number, user_id))
        await db.commit()


async def DB_var_ws(flag, user_id):
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        if flag == "correct":
            a = await db.execute('SELECT win_streak FROM variables WHERE user_id = ?', (user_id,))
            a = await a.fetchone()
            a = a[0] + 1
            if a == 5:
                await db.execute('UPDATE variables SET win_streak = 0 WHERE user_id = ?', (user_id,))
                await db.commit()
                return True
            else:
                await db.execute('UPDATE variables SET win_streak = ? WHERE user_id = ?',(a, user_id))
                await db.commit()
                return False

        elif flag == "incorrect":
            await db.execute('UPDATE variables SET win_streak = 0 WHERE user_id = ?', (user_id,))
            await db.commit()


async def main():
    # pass
    await DB()


if __name__ == "__main__":
    asyncio.run(main())