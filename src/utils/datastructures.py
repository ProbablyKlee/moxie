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
import asyncio

from typing import (
    List,
    Tuple,
    Any,
    Optional,
    Iterable,
    Awaitable,
    TypeVar,
    ParamSpec,
    MutableMapping,
)

from discord.utils import maybe_coroutine

T = TypeVar('T')
P = ParamSpec('P')

V = TypeVar("V")
K = TypeVar("K", bound=str)

__all__ = ('MaxSizedList', 'CaseInsensitiveDict')


class PartialCall(List[Any]):
    def append(self, rhs: Awaitable[Any]) -> None:
        super().append(rhs)

    def call(self, *args: Tuple[Any, ...], **kwargs: Any) -> asyncio.Future[List[Any]]:
        return asyncio.gather(*(maybe_coroutine(func, *args, **kwargs) for func in self))


class MaxSizedList:

    __slots__ = ("_list", "_max_size", "_index")

    def __init__(self, max_size: int) -> None:
        self._list: List[Any | None] = [None] * max_size
        self._max_size: int = max_size
        self._index: int = 0

    def push(self, item: Any) -> None:
        self._list[self._index % len(self._list)] = item
        self._index += 1

    def get_list(self) -> List[Any]:
        if self._index < self._max_size:
            return self._list[: self._index]
        return self._list[self._index % len(self._list) :] + self._list[: self._index % len(self._list)]

    def __iter__(self) -> Iterable[Any]:
        return iter(self.get_list())

    def __len__(self) -> int:
        return len(self.get_list())

    def __getitem__(self, index: int) -> Any:
        return self.get_list()[index]


class CaseInsensitiveDict(MutableMapping[K, V]):
    def __contains__(self, k: K) -> bool:
        return super().__contains__(k.casefold())

    def __delitem__(self, k: K) -> None:
        return super().__delitem__(k.casefold())

    def __getitem__(self, k: K) -> V:
        return super().__getitem__(k.casefold())

    def __setitem__(self, k: K, v: V) -> None:
        super().__setitem__(k.casefold(), v)

    def get(self, k: K, default: Optional[V] = None) -> V | None:
        return super().get(k.casefold(), default)

    def pop(self, k: K, default: Optional[V] = None) -> V | None:
        return super().pop(k.casefold(), default)
