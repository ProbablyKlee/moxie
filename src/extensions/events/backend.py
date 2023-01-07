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
import asyncio
import aiohttp

from typing import (
    TYPE_CHECKING,
    List,
    Dict,
    Optional,
    Sequence,
    Union,
)

import discord
from discord.ext import commands

from src.models import Guild, User
from src.base import BaseEventExtension

if TYPE_CHECKING:
    from src.classes import Context, RoboMoxie


class BackendEventHandler(BaseEventExtension):
    """Handles user and guild related events."""

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        members: Union[Sequence[discord.Member], List[discord.Member]] = (
            await guild.chunk(cache=True) if not guild.chunked else guild.members
        )

        await Guild.create_or_update(guild.id, True, 'owo', self.bot.pool)
        for_execution: Optional[List[discord.Member]] = []
        for m in members:
            try:
                if len(m.mutual_guilds) > 1:
                    continue
                elif m.bot:
                    continue
            except AttributeError:
                self.bot.logger.debug(f"Missing required attributes for {m!r}")
                continue
            else:
                for_execution.append(m)

        await User.insert_many(for_execution, self.bot.pool)
        del for_execution

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if (
            member.bot
            or member.guild.chunked
            or len(member.mutual_guilds) > 1
        ):
            return

        await User.create_or_update(member.id, self.bot.pool)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return  # No more stealing my precious storage space

        if before.name != after.name:
            self.bot.dispatch("user_name_change", before, after)

        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_change", before, after)

        if before.discriminator != after.discriminator:
            self.bot.dispatch("user_discriminator_change", before, after)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return

        if before.status != after.status:
            _: Dict[discord.Status, str] = {
                discord.Status.online: "online",
                discord.Status.idle: "idle",
                discord.Status.dnd: "dnd",
                discord.Status.offline: "offline",
            }

            # TODO: Database stuff
