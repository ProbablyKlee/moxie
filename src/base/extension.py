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

from typing import TYPE_CHECKING
from discord.ext import commands
from src.constants import Extension

if TYPE_CHECKING:
    from src.classes import RoboMoxie, Context

__all__ = ("BaseCommandExtension", "BaseEventExtension")


class BaseExtension(commands.Cog):
    """Base class for all extensions."""

    def __init__(self, bot: RoboMoxie) -> None:
        self.bot = bot


class BaseEventExtension(BaseExtension):
    """Base class for all event extensions."""

    @property
    def emoji(self) -> str:
        return Extension.EVENT


class BaseCommandExtension(BaseExtension):
    """Base class for all command extensions."""

    @property
    def emoji(self) -> str:
        raise NotImplementedError

    async def cog_check(self, ctx: Context[RoboMoxie]) -> bool:
        raise NotImplementedError
