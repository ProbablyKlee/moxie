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

import datetime
from typing import TYPE_CHECKING, ClassVar, Dict, Callable, Type, MutableSequence, Tuple, List

import copy
import asyncio
import itertools

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from src.classes import Context, RoboMoxie

from src.base import BaseEventExtension
from src.utils import TimeToLiveCache


class EventDispatcher(BaseEventExtension):
    """Dispatches events to the appropriate listeners."""

    def __init__(self, bot: RoboMoxie) -> None:
        super().__init__(bot)

        self.cached_ttl: TimeToLiveCache = TimeToLiveCache()
        self.error_handlers: Dict[Type[commands.CommandError], Callable[[Context, commands.CommandError], None]] = {
            commands.NoPrivateMessage: lambda *_: None,
            commands.DisabledCommand: lambda *_: None,
            commands.PrivateMessageOnly: lambda *_: None,
            commands.CommandNotFound: lambda ctx, error: self.bot.loop.create_task(
                self.handle_command_not_found(ctx, error)
            ),
            commands.MissingRequiredArgument: lambda ctx, error: self.bot.dispatch("missing_required_argument", ctx, error),
            commands.MemberNotFound: lambda ctx, error: self.bot.dispatch("member_not_found", ctx, error),
            commands.BadArgument: lambda ctx, error: self.bot.dispatch("bad_argument", ctx, error),
            commands.MissingPermissions: lambda ctx, error: self.bot.dispatch("missing_permissions", ctx, error),
            commands.BotMissingPermissions: lambda ctx, error: self.bot.dispatch("bot_missing_permissions", ctx, error),
            commands.CommandOnCooldown: lambda ctx, error: self.bot.dispatch("command_on_cooldown", ctx, error),
            commands.NotOwner: lambda ctx, error: self.bot.dispatch("not_owner", ctx, error),
        }

    def insert_user_rate_limit(self, user: discord.Member, rate_limit: int) -> None:
        self.cached_ttl.user_time_to_lives[user.id] = datetime.timedelta(seconds=rate_limit)

    def check_user_rate_limited(self, user: discord.Member) -> bool:
        time_to_live = self.cached_ttl.user_time_to_lives.get(user.id, None)
        if time_to_live:
            return user.id in self.cached_ttl.lrucache and self.cached_ttl.lrucache[user.id] > datetime.datetime.utcnow()
        return False

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError) -> None:

        # Has a local error handler
        if hasattr(ctx.command, "on_error"):
            return

        handler = self.error_handlers.get(
            type(error), lambda _ctx, _error: self.bot.logger.exception("Unhandled command error!", exc_info=error)
        )
        handler(ctx, error)

    async def handle_command_not_found(self, ctx: Context, _: commands.CommandError) -> None:
        command_sequence = []
        for command in [c for c in self.bot.commands if not c.hidden]:
            try:
                if await command.can_run(ctx):
                    command_sequence.append(([command.name].extend(command.aliases)))
            except Exception as exc:
                self.bot.logger.debug("Failed to check permissions for command %s", command.name, exc_info=exc)

        command_list = list(itertools.chain.from_iterable(command_sequence))  # type: ignore
        matches = self.bot.get_close_matches(ctx.invoked_with, command_list, cutoff=0.7)  # 0.7 is arbitrary

        if not matches:
            return

        confirm = await ctx.confirm(
            message=(
                f"Sorry, but the command **{ctx.invoked_with}** was not found.\n" f"**did you mean... `{matches[0]}`?**"
            ),
            delete_after_cancel=True,
            delete_after_confirm=True,
            delete_after_timeout=True,
            buttons=(('▶', f'execute {matches[0]}', discord.ButtonStyle.primary), ('🗑', None, discord.ButtonStyle.red)),
            timeout=30,
        )

        if confirm:
            message = copy.copy(ctx.message)
            message._edited_timestamp = discord.utils.utcnow()
            message.content = message.content.replace(ctx.invoked_with, matches[0])

            await self.bot.process_commands(message)
