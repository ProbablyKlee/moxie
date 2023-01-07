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
import imghdr
import asyncio
import aiohttp

from typing import Dict

import discord
from discord.ext import commands
from src.base import BaseEventExtension
from src.models import Guild, User


class BackendEventHandler(BaseEventExtension):
    """Handles user and guild related events."""

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        members = await guild.chunk(cache=True) if not guild.chunked else guild.members
        await Guild.create_or_update(guild.id, True, 'owo', self.bot.pool)

        for_execution = []
        avatar_images = []
        avatar_bytes = []
        for m in members:
            if len(m.mutual_guilds) > 1 or m.bot:
                continue
            try:
                avatar = await m.display_avatar.read()
            except discord.HTTPException:
                self.bot.logger.debug(f"Failed to get avatar for {m!r}")
                continue
            for_execution.append(m)
            avatar_images.append((m.id, "url", m.avatar.url))
            avatar_bytes.append((m.id, imghdr.what(None, avatar), avatar))

        await User.insert_many(for_execution, self.bot.pool)

        image_query = "SELECT insert_history_item($1, $2, $3"
        avatar_query = "SELECT insert_avatar_history_item($1, $2, $3, $4);"

        await self.bot.db.execute_many(image_query, avatar_images)
        await self.bot.db.execute_many(avatar_query, avatar_bytes)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot or member.guild.chunked or len(member.mutual_guilds) > 1:
            return

        await User.create_or_update(member.id, self.bot.pool)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return  # No more stealing my precious storage space

        if before.name != after.name:
            await User.insert_history_item(after, "name", after.name, self.bot.pool)
            self.bot.logger.debug(f"User {before!r} changed their name to {after!r}")

        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)
            self.bot.logger.debug(f"User {before!r} changed their avatar")

        if before.discriminator != after.discriminator:
            await User.insert_history_item(after, "discriminator", after.discriminator, self.bot.pool)
            self.bot.logger.debug(f"User {before!r} changed their discriminator")

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return

        if before.status != after.status:
            self.bot.logger.debug(f"User {before!r} changed their status to {after.status!r}")
            _: Dict[discord.Status, str] = {
                discord.Status.online: "online",
                discord.Status.idle: "idle",
                discord.Status.dnd: "dnd",
                discord.Status.offline: "offline",
            }

            # TODO: Database stuff
