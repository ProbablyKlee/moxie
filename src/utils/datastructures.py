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
    Any,
    Optional,
    Awaitable,
    TypeVar,
    Iterator,
    Mapping,
    MutableMapping,
)
from collections.abc import MutableSequence
from discord.utils import maybe_coroutine

V = TypeVar("V")
K = TypeVar("K", bound=str)

__all__ = ('MaxSizeList', 'InsensitiveMapping', 'PartialCall')


class PartialCall(List[Any]):
    def append(self, *rhs: List[asyncio.Task[Any]]) -> None:
        super().append(*rhs)

    def call(self, *args: Any, **kwargs: Any) -> asyncio.Future[List[Awaitable[Any]]]:
        return asyncio.gather(*(maybe_coroutine(func, *args, **kwargs) for func in self))


class MaxSizeList(MutableSequence[Any]):
    def __init__(self, max_size: int) -> None:
        self._max_size = max_size
        self._list: List[Any] = []

    def push(self, item: Any) -> None:
        if len(self) == self._max_size:
            self._list.pop(0)
        self._list.append(item)

    def __getitem__(self, index: int) -> Any:
        return self._list[index]

    def __setitem__(self, index: int, value: Any) -> None:
        self._list[index] = value

    def __delitem__(self, index: int) -> None:
        del self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} max_size={self._max_size} list={self._list!r}>"

    def __iter__(self) -> Iterator[Any]:
        return iter(self._list)

    def insert(self, index: int, value: Any) -> None:
        if len(self) == self._max_size:
            self._list.pop(0)
        self._list.insert(index, value)


class InsensitiveMapping(MutableMapping[K, V]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._dict: MutableMapping[str, V] = {}
        self.update(dict(*args, **kwargs))

    def __contains__(self, k: K) -> bool:
        return super().__contains__(k.casefold())

    def __delitem__(self, k: K) -> None:
        return super().__delitem__(k.casefold())

    def __getitem__(self, k: K) -> V:
        return super().__getitem__(k.casefold())

    def __setitem__(self, k: K, v: V) -> None:
        super().__setitem__(k.casefold(), v)

    def __iter__(self) -> Iterator[str | K]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def clear(self) -> None:
        self._dict.clear()

    def copy(self) -> "InsensitiveMapping[K, V]":
        """Return a shallow copy of this mapping."""
        return InsensitiveMapping(self._dict)

    def get(self, k: K, default: Optional[V] = None) -> V | None:
        return super().get(k.casefold(), default)

    def pop(self, k: K, default: Optional[V] = None) -> V | None:
        return super().pop(k.casefold(), default)

    def update(self, other: Mapping[K, V], **kwargs: Any) -> None:
        for key, value in other.items():
            self[key] = value
        for key, value in kwargs.items():
            self[key] = value  # type: ignore
