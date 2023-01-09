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
from typing import Any, OrderedDict, Callable
import datetime


class LruCache(OrderedDict):
    def __init__(self, maxsize: int, *args: Any, **kwargs: Any) -> None:
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: Any) -> Any:
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        if self.maxsize and len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class AsyncCache:
    def __init__(self, maxsize: int = 128) -> None:
        self.lrucache = LruCache(maxsize)

    def __call__(self, func: Callable) -> Callable:
        async def wrapper(*args: Any, use_cache=True, **kwargs: Any) -> Any:
            key = Key(args, kwargs)
            if key in self.lrucache and use_cache:
                return self.lrucache[key]

            self.lrucache[key] = await func(*args, **kwargs)
            return self.lrucache[key]

        wrapper.__name__ += func.__name__

        return wrapper


class TimeToLiveCache:
    class _TimeToLive(LruCache):
        def __init__(self, time_to_live: int, maxsize: int) -> None:
            super().__init__(maxsize=maxsize)

            self.time_to_live = datetime.timedelta(seconds=time_to_live) if time_to_live else None
            self.maxsize = maxsize

        def __contains__(self, key: Any) -> bool:
            if key not in self.keys():
                return False

            key_expiration = super().__getitem__(key)[1]
            if key_expiration and key_expiration < datetime.datetime.now():
                del self[key]
                return False

            return True

        def __getitem__(self, key: Any) -> Any:
            value = super().__getitem__(key)[0]
            return value

        def __setitem__(self, key: Any, value: Any) -> None:
            ttl_value = (datetime.datetime.now() + self.time_to_live) if self.time_to_live else None
            super().__setitem__(key, (value, ttl_value))

    def __init__(self, time_to_live: int = 60, maxsize: int = 1024, skip_args: int = 0) -> None:
        self.lrucache = self._TimeToLive(time_to_live, maxsize)
        self.skip_args = skip_args
        self.user_time_to_lives = {}

    def __call__(self, func: Callable) -> Callable:
        async def wrapper(*args, use_cache=True, **kwargs) -> Any:
            user_id = args[self.skip_args]
            key = user_id
            time_to_live = self.user_time_to_lives.get(user_id, self.lrucache.time_to_live)
            self.lrucache.time_to_live = time_to_live
            if key in self.lrucache and use_cache:
                return self.lrucache[key]

            self.lrucache[key] = await func(*args, **kwargs)
            return self.lrucache[key]

        wrapper.__name__ += func.__name__

        return wrapper


class Key:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        kwargs.pop("use_cache", None)

    def __hash__(self) -> int:
        def _hash(param: Any) -> Any:
            if isinstance(param, tuple):
                return tuple(map(_hash, param))
            if isinstance(param, dict):
                return tuple(map(_hash, param.items()))
            elif hasattr(param, "__dict__"):
                return str(vars(param))
            else:
                return str(param)

        return hash(_hash(self.args) + _hash(self.kwargs))
