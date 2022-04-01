from datetime import datetime, timedelta
from enum import Enum
from os import getenv
from typing import Optional

import aiosqlite
from disnake import User
from disnake.ext.commands import Bot
from dotenv import load_dotenv
from exencolorlogs import Logger

from modules.converters import Date

load_dotenv()


class SysData(Enum):
    daily_reset = "daily_reset"


class BdayBot(Bot):
    def __init__(self):
        super().__init__()
        self.log = Logger()
        self.db: aiosqlite.Connection = None

    def run(self):
        token = getenv("TOKEN")

        if token is None:
            self.log.warning(
                "The token is not provided. Please insert a new token and press [ENTER]:"
            )
            token = input()
            with open(".env", "w") as f:
                f.write(f"TOKEN={token}\n")

        self.log.info("Loading extensions...")
        self.load_extensions("./ext")
        super().run(token)

    async def start(self, *args, **kwargs):
        self.log.info("Establishing connection to the database...")
        self.db = await aiosqlite.connect("db.sqlite3")
        self.log.info("Connected to a database successfully!")

        self.log.info("Executing required SQL scripts...")
        with open("base_config.sql", "r") as f:
            for sql in f.read().split(";"):
                await self.execute(sql)
        if await self.get_sys_data(SysData.daily_reset) is None:
            await self.set_sys_data(SysData.daily_reset, 0)
        self.log.info("Successfully executed required SQL scripts!")

        self.log.info("Establishing connection to discord...")
        await super().start(*args, **kwargs)

    async def close(self):
        self.log.info("Closing database connection...")
        await self.db.close()
        await super().close()

    async def execute(self, query, *args) -> aiosqlite.Cursor:
        cur = await self.db.cursor()
        cur = await cur.execute(query, args)
        await self.db.commit()

        return cur

    async def on_ready(self):
        self.log.info("Bot has started successfully!")

    async def get_sys_data(self, sys_data: SysData):
        cur = await self.execute(f"SELECT {sys_data.value} FROM sys_data")
        r = await cur.fetchone()
        if r is None:
            return None

        return r[0]

    async def set_sys_data(self, sys_data: SysData, value):
        await self.execute(f"UPDATE sys_data SET {sys_data.value} = ?", value)

    async def get_reset(self):
        reset = await self.get_sys_data(SysData.daily_reset)
        return datetime.fromtimestamp(reset).date()

    async def update_reset(self):
        await self.set_sys_data(
            SysData.daily_reset, (datetime.now() + timedelta(days=1)).timestamp()
        )

    async def set_birthday(self, user: User, bday: Date):
        await self.execute(
            "INSERT OR REPLACE INTO users (id, birthday) VALUES (?, ?)",
            user.id,
            bday.to_str(),
        )

    async def get_birthday(self, user: User):
        cur = await self.execute("SELECT birthday FROM users WHERE id = ?", user.id)
        r = await cur.fetchone()
        if r is None:
            return None

        return r[0]

    async def get_birthdays_on_date(self, date: Date = None) -> "list[int]":
        date = date or Date.now()
        cur = await self.execute(
            "SELECT id FROM users WHERE birthday LIKE ?", date.to_short_str() + ".%"
        )
        rows = await cur.fetchall()
        return [r[0] for r in rows]

    async def get_guild_ids(self) -> "dict[int, Optional[int]]":
        cur = await self.execute("SELECT id, channel_id FROM guilds")
        rows = await cur.fetchall()
        return {r[0]: r[1] for r in rows}
