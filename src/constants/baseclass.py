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

__all__ = ("CONSTANTS",)


class ConstantsMeta(type):
    """Metaclass for constants."""

    @staticmethod
    def is_valid_constant(attr_name: str) -> bool:
        return attr_name.isupper() and all(c.isalpha() or c == '_' for c in attr_name)

    def __new__(mcs, name, bases, attrs):
        """Ensures that all constants are valid."""
        for attr_name, attr_value in attrs.items():
            if attr_name.startswith('__') and attr_name.endswith('__') or isinstance(attr_value, property):
                continue

            if not mcs.is_valid_constant(attr_name):
                raise ValueError(f"Attribute <{attr_name}> is not a valid constant")

        return super().__new__(mcs, name, bases, attrs)

    def __setattr__(self, attr: str, value: object):
        raise RuntimeError(f"Cannot assign to attribute <{attr}> of Constant object.")

    def __delattr__(self, attr: str):
        raise RuntimeError(f"Cannot delete attribute <{attr}> of Constant object")

    def __getitem__(self, attr: str):
        if hasattr(self, attr):
            return getattr(self, attr)
        raise KeyError(f"<{attr}> is not a valid key for Constant object")

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith('_'):
                yield attr

    def __len__(self):
        return sum(1 for _ in self)

    def __contains__(self, attr: str):
        return hasattr(self, attr)


class CONSTANTS(metaclass=ConstantsMeta):
    """Baseclass for constants.

    - This class serves as a base for defining constants in a subclass.
    - Constants defined in a subclass cannot be modified or deleted at runtime.
    - Constants defined in a subclass can be accessed as attributes or as dictionary keys.

    Examples
    --------
    >>> class MyConstants(CONSTANTS):
    ...     FOO = 'bar'
    ...
    ... constants = MyConstants()
    ... constants.FOO = 'baz'  # Raises a RuntimeError: 'Cannot assign to attribute <FOO> of Constant object.'
    ... del constants.FOO      # Raises a RuntimeError: 'Cannot delete attribute <FOO> of Constant object'
    ... constants.BAZ          # Raises an AttributeError: 'MyConstants' object has no attribute 'BAZ'
    ... 'FOO' in constants     # True
    ... 'BAZ' in constants     # False
    """

    pass  # The body of the class would go here, including any attributes and methods
