import asyncio
import aiosqlite


async def DB():
    async with aiosqlite.connect('EngBotDb.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                score INTEGER,
                tr_flag)''')
        await db.commit()


async def DB_add(user_id, username, first_name, last_name, score=0, tr_flag="0"):
    async with aiosqlite.connect('data/EngBotDb.db') as db:
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?',(user_id,))
        if not await cursor.fetchone():
            await db.execute('INSERT INTO users (user_id, username, first_name, last_name, score, tr_flag) VALUES(?,?,?,?,?,?)',
                             (user_id, username, first_name, last_name, score, tr_flag))
        else:
            print("already exists")
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


async def DB_leaderboard():
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        cursor = await db.execute('SELECT username, first_name, last_name, score FROM users ORDER BY score DESC LIMIT 10')
        board = await cursor.fetchall()
        result = ''
        smiles = ["🥇","🥈","🥉"]
        for index, user in enumerate(board):
            if not user[0] and not user[2]:
                result += f"#<b>{index + 1}</b> {user[1]}. Score: {user[3]}"
            elif not user[2]:
                result += f"#<b>{index + 1}</b> {user[1]} @{user[0]}. Score: {user[3]}"
            elif not user[0]:
                result += f"#<b>{index + 1}</b> {user[1]}. Score: {user[3]}\n\n"
            else: result += f"#<b>{index+1}</b> {user[1]} {user[2]} @{user[0]}. Score: {user[3]}"
            if len(smiles) > index:
                result += f"{smiles[index]}\n\n"
            else: result += "\n\n"
        return result


async def DB_select(flag, user_id):
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        a = await db.execute(f'SELECT {flag} FROM users WHERE user_id = ?',(user_id,))
        a = await a.fetchone()
        return a[0]


async def DB_insert(flag, number, user_id):
    async with aiosqlite.connect("data/EngBotDb.db") as db:
        await db.execute(f'UPDATE users SET {flag} = ? WHERE user_id = ?',(number, user_id))
        await db.commit()


async def main():
    pass
    # await DB()


if __name__ == "__main__":
    asyncio.run(main())
