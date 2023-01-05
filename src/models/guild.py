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
from typing import Sequence, List

import asyncpg
import discord


class Guild:
    """Represents a guild in the database."""

    def __init__(self, record: asyncpg.Record, pool: asyncpg.pool.Pool):
        self.pool = pool
        self.guild_id = record["guild_id"]
        self.score_counting = record["score_counting"]
        self.score_prefix = record["score_prefix"]

    @classmethod
    async def create_or_update(
        cls, guild_id: int, score_counting: bool, score_prefix: str, pool: asyncpg.pool.Pool
    ) -> Guild:
        record = await pool.fetchrow(
            """
            INSERT INTO guild (guild_id, score_counting, score_prefix)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id) DO UPDATE SET score_counting = $2, score_prefix = $3
            RETURNING *;
            """,
            guild_id,
            score_counting,
            score_prefix,
        )
        return cls(record, pool)

    @classmethod
    async def insert_many(cls, guilds: Sequence[discord.Guild], pool: asyncpg.pool.Pool) -> None:
        return await pool.executemany(
            """
            INSERT INTO guild (guild_id)
            VALUES ($1)
            ON CONFLICT DO NOTHING;
            """,
            ((guild.id,) for guild in guilds),
        )

    async def server_prefixes(self) -> List[str]:
        records = await self.pool.fetch("SELECT prefix FROM prefix WHERE guild_id = $1", self.guild_id)
        return [record["prefix"] for record in records] if records else []
