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
from typing import Sequence

import asyncpg
import discord


class User:
    """Represents a user in the database."""

    def __init__(self, record: asyncpg.Record, pool: asyncpg.pool.Pool):
        self.pool = pool
        self.user_id = record["user_id"]
        self.emoji_server_id = record["emoji_server_id"]

    @classmethod
    async def create_or_update(cls, user_id: int, emoji_server_id: int, pool: asyncpg.pool.Pool) -> User:
        record = await pool.fetchrow(
            """
            INSERT INTO users (user_id, emoji_server_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET emoji_server_id = $2
            RETURNING *;
            """,
            user_id,
            emoji_server_id,
        )
        return cls(record, pool)

    @classmethod
    async def insert_many(cls, users: Sequence[discord.Member], pool: asyncpg.pool.Pool) -> None:
        return await pool.executemany(
            """
            INSERT INTO users (user_id)
            VALUES ($1)
            ON CONFLICT DO NOTHING;
            """,
            ((u.id,) for u in users),
        )