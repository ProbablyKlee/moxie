# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2022-Present Lia Marie
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import io
import os
import re

import pathlib
import logging
import datetime
import itertools
import collections

from typing import Optional, Self, Union, Dict, List

import aiohttp
import asyncpg
import discord
from discord.ext import commands
from discord import Message, Interaction

from src.models import Guild, User
from src.config import Settings, Logger
from src.utils import PartialCall, InsensitiveMapping

from . import DatabaseConnector, Context

settings: Settings = Settings()  # type: ignore
formatter = Logger.get_formatter()
discord.utils.setup_logging(handler=logging.StreamHandler(), level=logging.INFO, formatter=formatter, root=True)


class RoboMoxie(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents(
            guilds=True,
            members=True,
            emojis=True,
            webhooks=True,
            presences=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(
            self.get_prefix, intents=intents, case_insensitive=True, owner_ids=[852419718819348510, 852419718819348510]
        )
        self.call: PartialCall = PartialCall()
        self.settings: Settings = settings

        self.version: str = "0.0.1"
        self.strip_after_prefix: bool = True

        self.uptime: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        self.logger: logging.Logger = logging.getLogger(__name__)

        # Variables which are set in the process of initializing the bot.
        self.session: Optional[aiohttp.ClientSession] = None
        self.pool: Optional[asyncpg.Pool] = None
        self.db: Optional[DatabaseConnector] = None

        # Cache
        self.cached_users: Dict[int, User] = {}
        self.cached_guilds: Dict[int, Guild] = {}
        self.cached_images: Dict[str, io.BytesIO] = {}
        self.cached_prefixes: Dict[int, List[str]] = {}
        self.cached_context: collections.deque[commands.Context["RoboMoxie"]] = collections.deque(maxlen=10)

    async def get_context(
        self,
        origin: Union[Message, Interaction],
        /,
        *,
        cls: type[Context] = Context,
    ) -> Union[Context | commands.Context[Self], None]:
        return await super().get_context(origin, cls=Context or cls)

    async def fill_user_cache(self) -> None:
        records = await self.db.fetch("SELECT * FROM users", simple=False)
        for record in records:
            if record["user_id"] in self.cached_users:
                continue

            user = User(record, self.db.pool)
            self.cached_users[user.user_id] = user

    async def fill_guild_cache(self) -> None:
        records = await self.db.fetch("SELECT * FROM guild", simple=False)
        for record in records:
            if record["guild_id"] in self.cached_guilds:
                continue

            guild = Guild(record, self.db.pool)
            self.cached_guilds[guild.guild_id] = guild

    async def fill_prefix_cache(self) -> None:
        records = await self.db.fetch("SELECT * FROM prefix", simple=False)
        self.cached_prefixes = {
            record["guild_id"]: [record["prefix"] for record in records if record["guild_id"] == record["guild_id"]]
            for record in records
        }

    async def get_prefix(self, message: discord.Message, /) -> Union[str, List[str]]:
        if not message.guild:
            if match := re.match(re.escape("fishie"), message.content, re.I):
                return match.group(0)

        if message.guild.id in self.cached_prefixes:
            regex = re.compile("|".join(map(re.escape, self.cached_prefixes[message.guild.id])), re.I)
            if match := regex.match(message.content):
                return match.group(0)

        return commands.when_mentioned(self, message)

    async def process_commands(self, message: discord.Message, /) -> None:

        ctx = await self.get_context(message)
        if ctx.valid and getattr(ctx.cog, 'qualified_name', None) != 'Myself':
            self.cached_context.append(ctx)
            await ctx.typing()

        return await super().process_commands(message)

    async def setup_hook(self) -> None:
        try:
            self.db: DatabaseConnector = DatabaseConnector(self)
            self.db.pool = await asyncpg.create_pool(
                user=settings.USER,
                password=settings.PASSWORD,
                database=settings.DATABASE,
                host=settings.HOST,
                port=settings.PORT,
            )
            self.session: aiohttp.ClientSession = aiohttp.ClientSession()

            await self.after_database_setup()
            await self.setup_extensions()

            # Cache related
            await self.fill_user_cache()
            await self.fill_guild_cache()
            await self.fill_prefix_cache()

        except Exception as exc:
            self.logger.exception("An error occurred while setting up the bot.", exc_info=exc)
        else:
            self.logger.info("Successfully set up the bot.")

    async def after_database_setup(self) -> None:
        prerequisite = pathlib.Path(__file__).parent.parent.parent / 'schemas' / 'prerequisite'
        essentials = pathlib.Path(__file__).parent.parent.parent / 'schemas' / 'essentials'
        directories = itertools.chain(prerequisite.glob('*.sql'), essentials.glob('*.sql'))

        for file in directories:
            try:
                await self.db.pool.execute(open(file, 'r').read())
            except Exception as exc:
                self.logger.exception("Failed to execute %s", file.name, exc_info=exc)

    async def setup_extensions(self) -> None:
        exclude = '_', '.'
        extensions = [file for file in os.listdir('src/extensions') if not file.startswith(exclude)]
        for extension in extensions:
            name = extension[:-3] if extension.endswith('.py') else extension
            try:
                await self.load_extension(f'source.extensions.{name}')
                self.logger.info(f"[{name.upper()}] Loaded successfully.")

            except Exception as exc:
                self.logger.exception(msg=f"[{name.upper()}] Failed to load.", exc_info=exc)

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def close(self) -> None:
        await super().close()

        if hasattr(self, 'session'):
            await self.session.close()

        if hasattr(self, 'db'):
            await self.db.pool.close()


moxie = RoboMoxie()
moxie._BotBase__cogs = InsensitiveMapping()


async def starter() -> None:
    async with moxie:
        await moxie.start(settings.TOKEN)
