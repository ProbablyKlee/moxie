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

import asyncio
import aiohttp
import logging

from typing import (
    TYPE_CHECKING,
    Optional,
    Callable,
    Literal,
    Tuple,
    Any,
)

import functools
import contextlib

import PIL
import discord

from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

from discord.ext import commands
from twemoji_parser import emoji_to_url

if TYPE_CHECKING:
    from . import RoboMoxie, MoxieEmbed

from src.utils import make_async

logger = logging.getLogger(__name__)
embed_only_kwargs = [
    "color",
    "colour",
    "title",
    "type",
    "description",
    "url",
    "timestamp",
    "fields",
    "field_inline",
]


class Context(commands.Context["RoboMoxie"]):
    """
    A subclass of :class:`discord.ext.commands.Context` with additional
    functionality.
    """

    message: discord.Message
    channel: discord.abc.Messageable

    @property
    def reference(self) -> discord.Message | Literal[False]:
        message = getattr(self, "reference", None)
        return isinstance(message, discord.Message) and message

    @property
    def referenced_member(self) -> discord.Member | discord.User | Literal[False]:
        message = self.reference
        return isinstance(message, discord.Message) and message.author

    @property
    def session(self) -> aiohttp.ClientSession | None:
        return self.bot.session

    @staticmethod
    async def to_shell_wrapper(command: str) -> Tuple[str, str]:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode()

    @staticmethod
    def check_buffer(buffer: BytesIO) -> Optional[BytesIO]:
        if (size := buffer.tell()) < 1:
            message: str = f"Received empty buffer (%s bytes)."
            logger.warning(message, size)
            raise commands.errors.BadArgument(message % size)
        elif (size := buffer.getbuffer().nbytes) > 10_000_000:
            message: str = f"Received buffer too large (%s bytes)."
            logger.warning(message, size)
            raise commands.errors.BadArgument(message % size)

        try:
            Image.open(buffer)
        except PIL.UnidentifiedImageError:
            message: str = f"Received buffer with unsupported image type."
            logger.warning(message)
            raise commands.errors.BadArgument(message)
        finally:
            buffer.seek(0)

        return buffer

    async def maybe_reply(
        self, content: Optional[str], mention_author: bool = False, **kwargs: Any
    ) -> discord.Message | None:
        await asyncio.sleep(0.05)
        with contextlib.suppress(discord.HTTPException):
            if self.message.reference:
                return await self.message.reference.resolved.reply(  # type: ignore
                    content=content,
                    mention_author=mention_author,
                    **kwargs,
                )
            else:
                return await self.send(content=content, **kwargs)

    async def wrap(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return await make_async(func)(*args, **kwargs)

    async def embed(
        self,
        content: Optional[str] = None,
        *,
        reply: bool = False,
        mention_author: bool = False,
        embed: Optional[discord.Embed] = None,
        **kwargs: Any,
    ) -> discord.Message | None:
        original_embed = MoxieEmbed.factory(self, **{k: v for k, v in kwargs.items() if k in embed_only_kwargs})

        if embed:
            new_embed = embed.to_dict()
            new_embed.update(original_embed.to_dict())  # type: ignore  # pyright: shut up
            original_embed = MoxieEmbed.from_dict(new_embed)

        to_send = (self.send, self.maybe_reply)
        if self.guild is not None and not self.channel.permissions_for(self.me).embed_links:
            message: str = "Embed links permission not found in %s (%s)."
            logger.warning(message, self.channel, self.guild)
            raise commands.BotMissingPermissions(["embed_links"])

        send_dict = {x: y for x, y in kwargs.items() if x not in embed_only_kwargs}
        return await to_send(content=content, mention_author=mention_author, embed=original_embed, **send_dict)  # type: ignore
