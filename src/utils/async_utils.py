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

from typing import Any
from collections import OrderedDict


class AsyncCache:
    def __init__(self, maxsize=128) -> None:
        """
        maxsize:
            Use maxsize as None for unlimited size cache
        """
        self.lrucache = LruCache(maxsize)

    def __call__(self, func) -> Any:
        async def wrapper(*args, use_cache=True, **kwargs):
            key = Key(args, kwargs)
            if key in self.lrucache and use_cache:
                return self.lrucache[key]

            self.lrucache[key] = await func(*args, **kwargs)
            return self.lrucache[key]

        wrapper.__name__ += func.__name__

        return wrapper


class AsyncTimeToLiveCache:
    class _TimeToLive(LruCache):
        def __init__(self, time_to_live, maxsize) -> None:
            super().__init__(maxsize=maxsize)

            self.time_to_live = (
                datetime.timedelta(seconds=time_to_live) if time_to_live else None
            )

            self.maxsize = maxsize

        def __contains__(self, key) -> bool:
            if key not in self.keys():
                return False

            key_expiration = super().__getitem__(key)[1]
            if key_expiration and key_expiration < datetime.datetime.now():
                del self[key]
                return False

            return True

        def __getitem__(self, key) -> Any:
            value = super().__getitem__(key)[0]
            return value

        def __setitem__(self, key, value) -> None:
            ttl_value = (
                (datetime.datetime.now() + self.time_to_live)
                if self.time_to_live
                else None
            )
            super().__setitem__(key, (value, ttl_value))

    def __init__(self, time_to_live=60, maxsize=1024, skip_args: int = 0) -> None:
        """
        time_to_live:
            Use time_to_live as None for non expiring cache
        maxsize:
            Use maxsize as None for unlimited size cache
        skip_args:
            Use `1` to skip first arg of func in determining cache key
        """
        self.ttl = self._TimeToLive(time_to_live=time_to_live, maxsize=maxsize)
        self.skip_args = skip_args

    def __call__(self, func) -> Any:
        async def wrapper(*args, use_cache=True, **kwargs):
            key = Key(args[self.skip_args:], kwargs)
            if key in self.ttl and use_cache:
                val = self.ttl[key]
            else:
                self.ttl[key] = await func(*args, **kwargs)
                val = self.ttl[key]

            return val

        wrapper.__name__ += func.__name__

        return wrapper


class Key:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        kwargs.pop("use_cache", None)

    def __eq__(self, obj) -> bool:
        return hash(self) == hash(obj)

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


class LruCache(OrderedDict):
    def __init__(self, maxsize, *args, **kwargs) -> None:
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __getitem__(self, key) -> Any:
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        if self.maxsize and len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
