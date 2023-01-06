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
import re
import math
import operator

from typing import Any, List, Union, NamedTuple

__all__ = ("Calculator", "Cube")


class OperatorInfo(NamedTuple):
    precedence: int
    associativity: str


_l, _r = 'left', 'right'
_ops = {
    '(': OperatorInfo(precedence=9, associativity=_l),
    '^': OperatorInfo(precedence=4, associativity=_r),
    '*': OperatorInfo(precedence=3, associativity=_l),
    '/': OperatorInfo(precedence=3, associativity=_l),
    '+': OperatorInfo(precedence=2, associativity=_l),
    '-': OperatorInfo(precedence=2, associativity=_l),
    ')': OperatorInfo(precedence=0, associativity=_l),
}
_num, _lparen, _rparen = 'NUMBER', '(', ')'


class Calculator:
    def __init__(self, expression: str):
        self.expression = expression

    def _tokenize(self) -> List[Union[str, Any]]:
        symbols = re.split(r'(\d+|\D)', self.expression)
        spaced_expression = ' '.join(symbols)

        tokens = spaced_expression.split()
        token_values = []
        for token in tokens:
            if token in _ops:
                token_values.append((token, _ops[token]))
            else:
                token_values.append((_num, token))
        return token_values

    @staticmethod
    def _parse_expression(tokens: List[Union[str, Any]]) -> List[str]:
        queue, stack = [], []
        for (
            token,
            value,
        ) in tokens:
            if token is _num:
                queue.append(value)
            elif token in _ops:
                t1, (p1, a1) = token, value
                while stack:
                    t2, (p2, a2) = stack[-1]
                    if (a1 == _l and p1 <= p2) or (a1 == _r and p1 < p2):
                        if t1 != _rparen:
                            if t2 != _lparen:
                                stack.pop()
                                queue.append(t2)
                            else:
                                break
                        else:
                            if t2 != _lparen:
                                stack.pop()
                                queue.append(t2)
                            else:
                                stack.pop()
                                break
                    else:
                        break
                if t1 != _rparen:
                    stack.append((t1, value))
        while stack:
            t2, (_, _) = stack[-1]
            stack.pop()
            queue.append(t2)
        return queue

    @staticmethod
    def _evaluate_rpn(tokens: List[str]) -> float:
        stack = []
        if len(tokens) == 1:
            return float(tokens[0])

        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
        }

        for token in tokens:
            if token not in ops:
                stack.append(token)
            else:
                secondary_operand = float(stack.pop())
                primary_operand = float(stack.pop())
                temp = ops[token](primary_operand, secondary_operand)

                if token == '/':
                    temp = math.trunc(temp)

                stack.append(temp)
        return stack.pop()

    def calculate(self) -> Union[float, int]:
        tokens = self._tokenize()
        rpn = self._parse_expression(tokens)
        result = self._evaluate_rpn(rpn)

        if result.is_integer():
            return int(result)
        return result

    def __repr__(self) -> str:
        return str(self.calculate())


class Cube:
    def __init__(self, size: int):
        self.size = size

    def get_grid_size(self) -> int:
        for i in range(1, self.size):
            if (i - 1) ** 2 < self.size <= i**2:
                return i

        return 2  # shouldn't happen

    def get_grid(self) -> List[List[int]]:
        grid = []
        for i in range(self.get_grid_size()):
            grid.append([])
            for j in range(self.get_grid_size()):
                grid[i].append(0)

        return grid

    def get_grid_center(self) -> tuple:
        grid = self.get_grid()
        return len(grid) // 2, len(grid) // 2
