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

from typing import TYPE_CHECKING, Dict, Callable, Any

import copy
import datetime
import itertools

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from src.classes import Context, RoboMoxie

from src.classes import MoxieEmbed
from src.utils import TimeToLiveCache
from src.base import BaseEventExtension


class EventDispatcher(BaseEventExtension):
    """Dispatches events to the appropriate listeners."""

    def __init__(self, bot: RoboMoxie) -> None:
        super().__init__(bot)

        self.cached_ttl: TimeToLiveCache = TimeToLiveCache()
        self.error_handlers: Dict[Any, Callable[[Context, commands.CommandError], None]] = {
            commands.errors.NoPrivateMessage: lambda *_: None,
            commands.errors.BotMissingPermissions: lambda *_: None,
            commands.errors.DisabledCommand: lambda *_: None,
            commands.errors.PrivateMessageOnly: lambda *_: None,
            commands.errors.NotOwner: lambda *_: None,
            commands.errors.CommandNotFound: lambda ctx, error: self.bot.loop.create_task(
                self.handle_command_not_found(ctx, error)
            ),
            commands.errors.CommandOnCooldown: lambda ctx, error: self.bot.loop.create_task(
                self.handle_command_on_cooldown(ctx, error)
            ),
            commands.errors.MissingRequiredArgument: lambda ctx, error: self.bot.loop.create_task(
                self.handle_required_argument(ctx, error)
            ),
            commands.errors.MemberNotFound: lambda ctx, error: self.bot.loop.create_task(
                self.handle_member_not_found(ctx, error)
            ),
            commands.errors.BadArgument: lambda ctx, error: self.bot.loop.create_task(self.handle_bad_argument(ctx, error)),
            commands.errors.MissingPermissions: lambda ctx, error: self.bot.loop.create_task(
                self.handle_missing_permissions(ctx, error)
            ),
        }

    def insert_user_rate_limit(self, user: discord.Member, rate_limit: int | float) -> None:
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
            type(error),
            lambda _ctx, _error: self.bot.logger.exception("Unhandled command at %s" % error.__cause__, exc_info=error),
        )
        handler(ctx, error)

    async def handle_command_not_found(self, ctx: Context, _: commands.CommandError) -> None:
        command_sequence = []
        for command in [c for c in self.bot.commands if not c.hidden]:
            try:
                if await command.can_run(ctx):
                    command_sequence.append(([command.name].extend(command.aliases)))
            except commands.CommandError as exc:
                self.bot.logger.debug("Failed to check permissions for command %s", command.name, exc_info=exc)

        command_list = list(itertools.chain.from_iterable(command_sequence))  # type: ignore
        matches = self.bot.get_close_matches(ctx.invoked_with, command_list, cutoff=0.7)  # 0.7 is arbitrary

        if not matches:
            return

        confirm = await ctx.confirm(
            message=(
                "Sorry, but the command **%s** was not found.\n"
                f"**did you mean... `%s`?**" % (ctx.invoked_with, matches[0])
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

    async def handle_command_on_cooldown(self, ctx: Context, error: commands.CommandOnCooldown) -> None:
        if self.check_user_rate_limited(ctx.author):
            return

        self.insert_user_rate_limit(ctx.author, error.retry_after)
        timestamp = discord.utils.format_dt(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=error.retry_after), style="R"
        )
        await ctx.send(
            "⏰ | %s, you are on cooldown. Try again in %s." % (ctx.author.mention, timestamp), delete_after=error.retry_after
        )

    @staticmethod
    async def handle_required_argument(ctx: Context, error: commands.MissingRequiredArgument) -> None:
        missing_argument = error.param.name
        signature = ctx.command.signature
        signature_split = signature.split(" ")

        command_usage = f"{ctx.command.name} "
        error_message = f' ' * len(ctx.command.name) + " "
        command_list: Dict[str, str] = {}

        previous = None
        for pos, val in enumerate(signature_split):
            key = val.replace('<', '').replace('>', '')
            if pos == 0:
                command_list[key] = '^' * len(key) if key == missing_argument else ' ' * len(key)
            else:
                if key == missing_argument:
                    command_list[key] = '^' * len(key)
                else:
                    if signature_split[pos - 1] == '<' + missing_argument + '>':
                        command_list[key] = '^' * len(key)
                        previous = key
                    else:
                        if previous:
                            if '^' in command_list[previous]:
                                command_list[key] = '^' * len(key)
                            else:
                                command_list[key] = ' ' * len(key)
                        else:
                            previous = signature_split[pos - 1].replace('<', '').replace('>', '')
                            if '^' in command_list[previous]:
                                command_list[key] = '^' * len(key)
                            else:
                                command_list[key] = ' ' * len(key)

        for key, val in command_list.items():
            command_usage += f"{key} "
            error_message += f"{val} "

        command = ctx.invoked_subcommand or ctx.command
        lineo = command.callback.__code__.co_firstlineno
        cog_display = command.cog.qualified_name if command.cog else 'unknown'

        spaces = ' ' * len(str(lineo))
        error_message += f'\n{spaces} |\n{spaces} |'

        embed = MoxieEmbed.factory(
            ctx=ctx,
            title="Oh no! moxie ran into an error :s",
            description=(
                "```sh\n"
                "error: missing required argument\n"
                f"{spaces}--> $ext/{cog_display.lower()}.py:{lineo}:{lineo + 1}\n"
                f"{spaces} |\n"
                f"{lineo} | ::{command_usage}\n"
                f"{lineo + 1} |   {error_message}\n"
                f"{spaces} | => {ctx.command.brief}\n"
                f"{spaces} |\n"
                f"{spaces} | => For more information use help {ctx.command.name}"
                "```"
            ),
        )
        await ctx.send(embed=embed)

    @staticmethod
    async def handle_member_not_found(ctx: Context, error: commands.MemberNotFound) -> None:
        failed_to_convert = error.argument
        spaces = ' ' * len(str(ctx.command.callback.__code__.co_firstlineno))
        embed = MoxieEmbed.factory(
            ctx=ctx,
            title="moxie could not find what you were looking for :s",
            description=(
                "```sh\n"
                f"error: member not found\n"
                f"{spaces} |\n"
                f"{spaces} | => {failed_to_convert} is not a valid member\n"
                f"{spaces} |\n"
                f"{spaces} | => For more information use help {ctx.command.name}"
                "```"
            ),
        )
        await ctx.send(embed=embed)

    @staticmethod
    async def handle_bad_argument(ctx: Context, error: commands.BadArgument) -> None:
        await ctx.send("⚠ | %s, %s" % (ctx.author.mention, error))

    @staticmethod
    async def handle_missing_permissions(ctx: Context, error: commands.MissingPermissions) -> None:
        lineo = error.__traceback__.tb_frame.f_lineno
        spaces = ' ' * len(str(lineo + 1))

        title = ("Looks like you don't have the permissions to do that :s",)
        description = (
            "```sh\n"
            "error: missing permissions\n"
            f"{spaces} |--> $commands.MissingPermissions:{lineo}:{lineo + 1}\n"
            f"{spaces} |\n"
            f"{lineo} | => {ctx.command.name} requires the following permissions:\n"
        )

        for perm in error.missing_permissions:
            description += f"{spaces} | >> {perm}\n"

        description += f"{spaces} |\n" f"{spaces} | => For more information use help {ctx.command.name}"

        embed = MoxieEmbed.factory(
            ctx=ctx,
            title=title,
            description=description,
        )
        await ctx.send(embed=embed)
