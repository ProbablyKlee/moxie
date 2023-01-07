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
from typing import Sequence, TYPE_CHECKING

import asyncpg
import discord

if TYPE_CHECKING:
    from src.classes import RoboMoxie


class User:
    """Represents a user in the database."""

    def __init__(self, record: asyncpg.Record, bot: RoboMoxie) -> None:
        self.bot = bot
        self.user_id = record["user_id"]
        self.emoji_server_id = record["emoji_server_id"]

    @classmethod
    async def insert_maybe_user(cls, user_id: int, bot: RoboMoxie) -> None:
        await bot.db.fetch(
            """
            INSERT INTO users (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING;
            """,
            user_id,
            simple=True,
        )

    @classmethod
    async def insert_many(cls, users: Sequence[discord.Member], bot: RoboMoxie) -> None:
        return await bot.db.execute_many(
            """
            INSERT INTO users (user_id)
            VALUES ($1)
            ON CONFLICT DO NOTHING;
            """,
            ((u.id,) for u in users),
        )

    @classmethod
    async def insert_history_item(cls, user: discord.Member, user_type: str, entry_type: str, bot: RoboMoxie) -> None:
        await bot.db.execute("SELECT insert_history_item($1, $2, $3);", user.id, user_type, entry_type)

    @classmethod
    async def insert_avatar_history_item(
        cls, user: discord.Member, p_format: str, avatar: bytes, bot: RoboMoxie
    ) -> None:
        await bot.db.execute("SELECT insert_avatar_history_item($1, $2, $3, $4);", user.id, p_format, avatar)

    async def fetch_history(self, user_type: str) -> list[dict[str, ...]]:
        return await self.bot.db.fetch(
            """
            SELECT * FROM user_history
            WHERE user_id = $1 AND user_type = $2
            ORDER BY added_at DESC
            """,
            self.user_id,
            user_type,
            simple=False,
        )

    async def fetch_avatar_history(self) -> list[dict[str, ...]]:
        return await self.bot.db.fetch(
            """
            SELECT * FROM avatar_history
            WHERE user_id = $1
            ORDER BY added_at DESC
            """,
            self.user_id,
            simple=False,
        )
