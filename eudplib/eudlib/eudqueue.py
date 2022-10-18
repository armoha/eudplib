#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Armoha

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

from ..core import (
    Add,
    AtLeast,
    EUDFunc,
    EUDVariable,
    EUDVArray,
    Exactly,
    Forward,
    Memory,
    RawTrigger,
    SetMemory,
    SetTo,
    VProc,
)
from ..core.eudfunc.eudf import _EUDPredefineParam
from ..utils import EPD, cachedfunc, ep_assert


@cachedfunc
def EUDQueue(capacity):
    ep_assert(isinstance(capacity, int))

    class _EUDQueue:
        def __init__(self):
            ret = EUDVariable()
            pop = ret.SetNumber(0)
            queue = EUDVArray(capacity)(dest=EPD(pop) + 5, nextptr=pop - 328)
            append_action = SetMemory(queue + 348, SetTo, 0)
            jump = Forward()
            tail = EUDVariable(queue)

            @_EUDPredefineParam((EPD(append_action) + 5,))
            @EUDFunc
            def append(value):
                RawTrigger(
                    actions=[
                        append_action,
                        SetMemory(append_action + 16, Add, 18),
                        tail.AddNumber(72),
                    ],
                )
                RawTrigger(
                    conditions=tail.AtLeast(queue + 72 * capacity),
                    actions=[
                        SetMemory(append_action + 16, SetTo, EPD(queue) + 87),
                        tail.SetNumber(queue),
                    ],
                )

            @EUDFunc
            def popleft():
                nonlocal jump, ret, pop
                jump << RawTrigger(nextptr=queue)
                RawTrigger(
                    actions=[
                        pop,
                        SetMemory(jump + 4, Add, 72),
                    ],
                )
                RawTrigger(
                    conditions=Memory(jump + 4, AtLeast, queue + 72 * capacity),
                    actions=SetMemory(jump + 4, SetTo, queue),
                )
                return ret

            def empty():
                is_empty = Memory(jump + 4, Exactly, 0)
                VProc(tail, tail.SetDest(EPD(is_empty) + 5))
                return is_empty

            self._append = append
            self._popleft = popleft
            self._empty = empty

        def append(self, value, **kwargs):
            self._append(value, **kwargs)

        def popleft(self, **kwargs):
            return self._popleft(**kwargs)

        def empty(self, **kwargs):
            return self._empty(**kwargs)

    return _EUDQueue
