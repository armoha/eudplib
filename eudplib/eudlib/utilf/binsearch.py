#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from eudplib import core as c
from eudplib import ctrlstru as cs


def EUDBinaryMax(cond, minv: int = 0, maxv: int = 0xFFFFFFFF) -> c.EUDVariable:
    """Find maximum x satisfying cond(x) using binary search

    :param cond: Test condition
    :param minv: Minimum value in domain
    :param maxv: Maximum value in domain

    Cond should be binary classifier, meaning that for some N
        for all x > N, cond(x) is false.
        for all x <= N, cond(x) is true
    Then EUDBinaryMin will find such N.

    .. note:: If none of the value satisfies condition, then this
        function will return maxv.
    """
    if isinstance(minv, int) and isinstance(maxv, int):
        assert minv <= maxv
        r = maxv - minv
        if r == 0:
            return minv

    else:
        r = None

    x = c.EUDVariable()
    nth = 0
    for i in range(31, -1, -1):
        if r and 2**i > r:
            continue

        if nth == 0:
            x << minv + 2**i
            if cs.EUDIfNot()(cond(x)):
                cs.DoActions(x.SubtractNumber(2**i))
            cs.EUDEndIf()
        else:
            x += 2**i
            if cs.EUDIfNot()([x <= maxv, cond(x)]):
                cs.DoActions(x.SubtractNumber(2**i))
            cs.EUDEndIf()
        nth += 1

    return x


def EUDBinaryMin(cond, minv: int = 0, maxv: int = 0xFFFFFFFF) -> c.EUDVariable:
    """Find minimum x satisfying cond(x) using binary search

    :param cond: Test condition
    :param minv: Minimum value in domain
    :param maxv: Maximum value in domain

    Cond should be binary classifier, meaning that for some N
        for all x < N, cond(x) is false.
        for all x >= N, cond(x) is true
    Then EUDBinaryMin will find such N

    .. note:: If none of the value satisfies condition, then this
        function will return maxv.
    """
    if isinstance(minv, int) and isinstance(maxv, int):
        assert minv <= maxv
        r = maxv - minv
        if r == 0:
            return minv
    else:
        r = None

    x = c.EUDVariable()
    nth = 0
    for i in range(31, -1, -1):
        if r and 2**i > r:
            continue

        if nth == 0:
            x << maxv - 2**i
            if cs.EUDIfNot()(cond(x)):
                x += 2**i
            cs.EUDEndIf()
        else:
            if cs.EUDIf()(x >= 2**i):
                cs.DoActions(x.SubtractNumber(2**i))
                if cs.EUDIfNot()([x >= minv, cond(x)]):
                    x += 2**i
                cs.EUDEndIf()
            cs.EUDEndIf()
        nth += 1

    return x
