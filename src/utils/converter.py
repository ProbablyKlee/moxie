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
import typing
import logging
import discord

from discord.ext import commands
from discord.ext.commands import Converter, Context

__all__ = ("MaybeMember",)
logger = logging.getLogger(__name__)


class MaybeMember(Converter):

    """A custom Member converter that allows for partial matches.

    This inherits from :class:`discord.ext.commands.Converter` and overrides
    the :meth:`discord.ext.commands.Converter.convert` method.

    Examples
    --------
    >>> @commands.command()
    ... async def example(self, ctx: Context, member: MaybeMember):
    ...     await ctx.send(f"Member: {member}")
    ...
    """

    async def convert(self, ctx: Context, argument: str) -> typing.Optional[discord.Member]:
        """|coro|

        Transforms the argument into a :class:`discord.Member` or :class:`None`.

        Parameters
        ----------
        ctx: :class:`discord.ext.commands.Context` (or subclass)
            The context of the command.

        argument: :class:`str`
            The argument to convert.

        Returns
        -------
        :class:`discord.Member` or :class:`None`
            The member or :data:`None` if not found.

        Raises
        ------
        :exc:`discord.ext.commands.errors.MemberNotFound`
            The member was not found.
        """
        try:
            member = await commands.MemberConverter().convert(ctx, argument)
        except commands.errors.MemberNotFound:
            members = await ctx.guild.query_members(query=argument, limit=1)
            member = members[0] if members else None
        if member is None:
            logger.debug("Member not found: %s", argument)
            raise commands.errors.MemberNotFound(argument)
        return member
