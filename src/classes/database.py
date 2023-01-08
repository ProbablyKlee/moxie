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

from typing import TYPE_CHECKING, Optional, Any, List, Dict, Union

import collections

if TYPE_CHECKING:
    from . import RoboMoxie


class DatabaseConnector:
    def __init__(self, bot: RoboMoxie) -> None:
        self.bot = bot
        self.pool = self.bot.pool

    async def execute(self, query: str, *args: Any) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(query, *args)

    async def execute_many(self, query: str, *args: Any) -> None:
        async with self.pool.acquire() as connection:
            await connection.executemany(query, *args)

    async def fetch(
        self, query: str, *args: Any, simple: bool = True
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        async with self.pool.acquire() as connection:
            if simple:
                return await connection.fetchrow(query, *args)
            return await connection.fetch(query, *args)

    async def table(self, table: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        tables: Dict[str, Dict[str, int]] = collections.defaultdict(dict)
        for record in await self.fetch(  # type: ignore
            """
                SELECT * FROM information_schema.columns
                WHERE $1::TEXT IS NULL OR table_name = $1::TEXT
                ORDER BY
                table_schema = 'pg_catalog' ASC,
                table_schema = 'information_schema' ASC,
                table_catalog ASC,
                table_schema ASC,
                table_name ASC,
                ordinal_position ASC
                """,
            table,
            simple=False,
        ):
            table_name: str = f"{record['table_catalog']}.{record['table_schema']}.{record['table_name']}"
            tables[table_name][record['column_name']] = record['data_type'].upper() + (  # type: ignore
                ' NOT NULL' if record['is_nullable'] == 'NO' else ''
            )

        return tables
