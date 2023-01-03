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
import functools

from concurrent.futures import ThreadPoolExecutor
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
    Type,
    Any,
)

from discord.app_commands import Command as AppCommand
from discord.ext.commands import Command as ExtCommand

T = TypeVar("T")
P = ParamSpec("P")
executor = ThreadPoolExecutor()


__all__ = (
    "make_async",
    "for_all_callbacks",
)


def make_async(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Decorator to wrap a function in a coroutine."""

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.get_event_loop().run_in_executor(executor, functools.partial(func, *args, **kwargs))

    return wrapper


def for_all_callbacks(decorator: Any) -> Any:

    """
    Decorator factory that applies the provided decorator to all methods of a class
    that are instances of either AppCommand or ExtCommand.
    """

    def decorate(cls: Type[T]) -> Type[T]:
        for attr in cls.__dict__:
            method = getattr(cls, attr)
            if isinstance(method, (AppCommand, ExtCommand)):
                setattr(cls, attr, decorator(method))

        return cls

    return decorate
