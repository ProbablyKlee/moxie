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

import re
import uuid
import imghdr
import asyncio
import aiohttp
import datetime

from typing import ClassVar, Dict

import discord
from discord.ext import commands

from src.config import Settings
from src.models import Guild, User
from src.base import BaseEventExtension

__all__ = ("BackendEventHandler",)
settings: Settings = Settings()  # type: ignore


class BackendEventHandler(BaseEventExtension):
    """Handles user and guild related events."""

    status_text: ClassVar[Dict[discord.Status, str]] = {
        discord.Status.online: "online",
        discord.Status.idle: "idle",
        discord.Status.dnd: "dnd",
        discord.Status.offline: "offline",
    }

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        members = await guild.chunk(cache=True) if not guild.chunked else guild.members
        await Guild.create_or_update(guild.id, True, 'owo', self.bot)

        for_execution = []
        avatar_images = []
        avatar_bytes = []
        for m in members:
            try:
                if len(m.mutual_guilds) > 1 or m.bot:
                    continue
            except AttributeError:
                self.bot.logger.debug(f"Member {m} from guild {guild} was skipped due to AttributeError.")
                continue
            try:
                avatar = await m.display_avatar.read()
            except discord.HTTPException:
                self.bot.logger.debug(f"Failed to get avatar for {m!r}")
                continue
            for_execution.append(m)
            avatar_images.append((m.id, "url", m.avatar.url))
            avatar_bytes.append((m.id, imghdr.what(None, avatar), avatar))

        await User.insert_many(for_execution, self.bot)

        image_query = "SELECT insert_history_item($1, $2, $3);"
        avatar_query = "SELECT insert_avatar_history_item($1, $2, $3);"

        await self.bot.db.execute_many(image_query, avatar_images)
        await self.bot.db.execute_many(avatar_query, avatar_bytes)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot or member.guild.chunked or len(member.mutual_guilds) > 1:
            return

        await User.insert_maybe_user(member.id, self.bot)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return  # No more stealing my precious storage space

        if before.name != after.name:
            await User.insert_history_item(after, "name", after.name, self.bot)
            self.bot.logger.debug(f"User {before!r} changed their name to {after!r}")

        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)
            self.bot.logger.debug(f"User {before!r} changed their avatar")

        if before.discriminator != after.discriminator:
            await User.insert_history_item(after, "discriminator", after.discriminator, self.bot)
            self.bot.logger.debug(f"User {before!r} changed their discriminator")

    @commands.Cog.listener()
    async def on_user_avatar_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return  # Naughty bots

        transcript = await self.bot.get_or_fetch_channel(settings.TRANSCRIPT_CHANNEL)

        try:
            avatar = await after.display_avatar.read()
        except discord.HTTPException as exc:
            self.bot.logger.debug(f"Failed to get avatar for {after!r} ({exc.code})")
            return

        await self.bot.db.execute(
            "SELECT insert_avatar_history_item($1, $2, $3);", after.id, imghdr.what(None, avatar), avatar
        )

        if transcript is not None:
            filename = f"{uuid.uuid4().hex[:16]}.png"
            message = await transcript.send(file=discord.File(avatar, filename=filename), content="free real estate")
            await User.insert_history_item(after, "url", message.attachments[0].url, self.bot)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return

        if before.status != after.status:
            query = """
                    INSERT INTO activity_history (
                        user_id,
                        seconds_{},
                        seconds_{},
                        last_update, last_status)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id)
                    DO UPDATE SET 
                        seconds_{} = activity_history.seconds_{} + 
                        EXTRACT(EPOCH FROM ($4 - activity_history.last_update)),
                        last_update = $4, 
                        last_status = $5
                """.format(
                self.status_text[before.status],
                self.status_text[after.status],
                self.status_text[before.status],
                self.status_text[after.status],
            )

            await self.bot.db.execute(
                query, before.id, 0, 0, datetime.datetime.now(tz=datetime.timezone.utc), self.status_text[after.status]
            )
