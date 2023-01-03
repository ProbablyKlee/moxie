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
from contextlib import AbstractContextManager
from types import TracebackType
from typing import (
    Type,
    Any,
    Optional,
    Self,
)

import logging

__all__ = ("suppress",)
logger = logging.getLogger(__name__)


class suppress(AbstractContextManager[None]):

    """Suppresses any exceptions that are raised within the context.

    This inherits from :class:`contextlib.AbstractContextManager`.

    Examples:
    --------
    >>> with suppress(ValueError, log="whatever {wotnot}", wotnot="I don't know"):
    ...      ...

    Notes:
    -----
    Note that you should **NOT** use `return` within the context of `suppress()`. Instead,
    use The Single Return Law pattern. This is because static analysis tools will not
    be able to understand that code following the context is reachable.
    """
    def __init__(self, *exceptions: Type[BaseException], log: str, **kwargs: Any) -> None:
        self._exceptions = exceptions
        self._log = log
        self._kwargs = kwargs

    def __enter__(self) -> Self:
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]] = None,
            exc_value: Optional[BaseException] = None,
            traceback: Optional[TracebackType] = None
    ) -> Optional[bool]:
        if captured := exc_type is not None and issubclass(exc_type, self._exceptions):

            logger.info(self._log.format(**self._kwargs))

        return captured
