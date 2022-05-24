from db import *
import hikari
import lightbulb
from datetime import datetime
from lightbulb.ext import tasks
from aiohttp import ClientSession
import os
import miru
from dotenv import load_dotenv

load_dotenv()

def get_token(): return os.getenv("TOKEN")

class Dark(lightbulb.BotApp):
    def __init__(self) -> lightbulb.BotApp:
        self.http = ClientSession()
        self.eco = Bank()
        self.xp = Experience()
        self.channels = Channels()
        self.warns = Warns()
        self.info = Info()

        super().__init__(token=get_token(), prefix="!", ignore_bots=True, owner_ids=[925079016174682213], help_slash_command=True, intents=hikari.Intents.ALL)
        self._boot = datetime.utcnow()
        self.load_extensions_from('./extensions')
        tasks.load(self)
        self.event_manager.subscribe(hikari.StartingEvent, self.setup)

    async def setup(self, _: hikari.StartingEvent):
        await self.eco.setup()
        await self.xp.setup()
        await self.channels.setup()
        await self.warns.setup()
        await self.info.setup()

bot = Dark()
miru.load(bot)

bot.run()