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
import datetime

from typing import (
    TYPE_CHECKING,
    Optional,
    Iterable,
    Union,
    Tuple,
    Any,
)

from discord import utils, Embed, Color

if TYPE_CHECKING:
    from . import Context


from src.constants import Colours


class MoxieEmbed(Embed):
    """A subclass of :class:`discord.Embed` with additional functionality."""

    def __init__(
        self,
        colour: Optional[Union[Color, int]] = Colours.EMBED,
        timestamp: Optional[datetime.datetime] = None,
        fields: Optional[Iterable[Tuple[str, str, bool]]] = (),
        **kwargs: Any,
    ) -> None:
        """Initialize the embed with the given attributes."""
        super().__init__(colour=colour, timestamp=timestamp, **kwargs)

        if fields:
            for name, value, inline in fields:
                self.add_field(name=name, value=value, inline=inline)

    @classmethod
    def factory(cls, ctx: "Context", **kwargs: Any) -> "MoxieEmbed":
        """Base factory method for creating an embed."""
        instance = cls(timestamp=utils.utcnow(), **kwargs)
        instance.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        return instance

    @classmethod
    def action(cls, title: str, gif: str, footer: str, **kwargs: Any) -> "MoxieEmbed":
        """Factory method for creating an embed for an action."""
        instance = cls(title=title, **kwargs)
        instance.set_image(url=gif)
        instance.set_footer(text=footer)
        return instance
