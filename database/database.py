import aiosqlite
from aiosqlite import Row
from collections.abc import Iterable

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

    async def getUsers(self) -> tuple[Iterable[Row], Iterable[Row]]:
        async with self.conn.execute("SELECT vk_id, user_secret FROM vk_users") as c:
            vk_result = await c.fetchall()
        async with self.conn.execute("SELECT tg_id, user_secret FROM tg_users") as c:
            tg_result = await c.fetchall()

        return vk_result, tg_result

    async def createUser(self, mes: str, mes_id: int, user_secret: str):
        async with self.conn.execute_insert(
            f"""INSERT INTO {mes}_users({mes}_id, user_secret) VALUES(?, ?)""", (mes_id, user_secret)
            ) as _:
            await self.conn.commit()

    async def getUserID(self, mes:str, secret: str) -> int:
        async with self.conn.execute(f"SELECT {mes}_id FROM {mes}_users WHERE user_secret=?", (secret, )) as c:
            row = await c.fetchone()
            if row != None:
                return row[0]
        return 0

    async def addChat(self, user_secret: str, who_secret:str, chat_name: str):
        async with self.conn.execute(
            'INSERT INTO p2p(user_secret, who_secret, chat_name)VALUES(?, ?, ?)', 
            (user_secret, who_secret, chat_name)) as _:
            await self.conn.commit()

db = DataBase("db.db")
