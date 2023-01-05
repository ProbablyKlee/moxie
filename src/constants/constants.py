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
import regex

from typing import Type
from discord import Object
from discord.abc import Snowflake

from .baseclass import CONSTANTS

__all__ = ('Colours', 'RMoxie', 'Ext', 'Regex', 'Bots', 'Emojis')


class Colours(CONSTANTS):

    EMBED: int = 0xFFCCB4


class RMoxie(CONSTANTS):

    GUILD_ID: int = 802227019203084298

    @property
    def thumb_url(self) -> str:
        return self.avatar_url  # maybe change this later

    @property
    def avatar_url(self) -> str:
        return f"https://cdn.discordapp.com/attachments/1059817715583430667/1059825225451184228/rmoxie_av.png"

    @property
    def guild_object(self) -> Snowflake:
        return Object(id=self.GUILD_ID)


class Regex(CONSTANTS):

    EMOJI: Type[regex.Pattern] = regex.compile(r'((?<!<a?))?:(?P<name>\w+):(?(1)|(?!\d+>))')
    MARKDOWN: Type[regex.Pattern] = regex.compile(r'(?<!`)(`+)(?!`)([\\s\\S]+?)(?<!`)\\1(?!`)')


class Bots(CONSTANTS):

    OWO: int = 408785106942164992


class Emojis(CONSTANTS):

    STOP: str = "<:please_stop:1057473529437765653>"


class Ext(CONSTANTS):

    ...
