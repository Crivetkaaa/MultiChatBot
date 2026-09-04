import aiosqlite
from aiosqlite import Row
from collections.abc import Iterable
from config import max_keyboards_len

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

    async def getUsers(self, mes: str) -> tuple[Iterable[Row], Iterable[Row]]:
        async with self.conn.execute(f"SELECT {mes}_id, user_secret FROM {mes}_users") as c:
            result = await c.fetchall()
        return result

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

    async def addChat(self, user_secret: str, who_secret: str, chat_name: str):
        await self.conn.execute(
            """
            INSERT INTO p2p (user_secret, who_secret, chat_name) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_secret, who_secret) 
            DO UPDATE SET chat_name = excluded.chat_name;
            """, 
            (user_secret, who_secret, chat_name)
        )
        await self.conn.commit()

    async def getChats(self, user_secret: str, last_id: int=0) -> Iterable[Row] | None:
        async with self.conn.execute(
            """SELECT id, who_secret, chat_name
            FROM p2p
            WHERE user_secret = ?
            AND id > ?
            ORDER BY id
            LIMIT ?
            """,
            (user_secret, last_id, max_keyboards_len)
        ) as c:
            rows = await c.fetchall()
            return rows
        return None

db = DataBase("db.db")
