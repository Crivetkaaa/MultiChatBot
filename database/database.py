import aiosqlite

class DataBase:

    def __init__(self, path: str):
        self.db_path = path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)

        text = None
        with open("database\command.sql") as file:
            text = file.read()
        await self.conn.executescript(text) 
        await self.conn.commit()

    async def getUsers(self):
        async with self.conn.execute("SELECT vk_id, user_secret FROM vk_users") as c:
            vk_result = await c.fetchall()
        async with self.conn.execute("SELECT tg_id, user_secret FROM tg_users") as c:
            tg_result = await c.fetchall()

        return vk_result, tg_result

    async def createUser(self, mes: str, mes_id: int, user_secret: str):
        user_id = None
        async with self.conn.execute_insert(F'INSERT INTO users(user_secret) VALUES(?)', (user_secret,)) as c:
            user_id = c[0]
            await self.conn.commit()

        async with self.conn.execute_insert(
            f"""INSERT INTO {mes}_users(user_id, {mes}_id, user_secret) VALUES(?, ?, ?)""", (user_id, mes_id, user_secret)
            ) as c:
            await self.conn.commit()

    async def getUserID(self, mes:str, secret: str) -> int:
        async with self.conn.execute(f"SELECT {mes}_id FROM {mes}_users WHERE user_secret=?", (secret, )) as c:
            row = await c.fetchone()
            if row != None:
                return row[0]

db = DataBase("db.db")