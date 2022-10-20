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
    AtMost,
    EUDFunc,
    EUDVariable,
    EUDVArray,
    Exactly,
    Forward,
    Memory,
    NextTrigger,
    PopTriggerScope,
    PushTriggerScope,
    RawTrigger,
    SetMemory,
    SetNextPtr,
    SetTo,
    VProc,
)
from ..core.eudfunc.eudf import _EUDPredefineParam
from ..ctrlstru import EUDEndWhile, EUDWhile
from ..utils import EPD, cachedfunc, ep_assert


@cachedfunc
def EUDQueue(capacity):
    """A single-ended queue implemented with a fixed-size variable array."""
    ep_assert(isinstance(capacity, int) and capacity > 0)

    class _EUDQueue:
        def __init__(self):
            ret = EUDVariable()
            pop = ret.SetNumber(0)
            queue = EUDVArray(capacity)(dest=EPD(pop) + 5, nextptr=pop - 328)
            append_action = SetMemory(queue + 348, SetTo, 0)
            jump = Forward()
            self._length = EUDVariable(0)

            @_EUDPredefineParam((EPD(append_action) + 5,))
            @EUDFunc
            def append(value):
                RawTrigger(
                    actions=[
                        append_action,
                        SetMemory(append_action + 16, Add, 18),
                    ],
                )
                RawTrigger(
                    conditions=Memory(
                        append_action + 16, AtLeast, EPD(queue) + 87 + 18 * capacity
                    ),
                    actions=SetMemory(append_action + 16, SetTo, EPD(queue) + 87),
                )
                RawTrigger(
                    conditions=self._length.AtMost(capacity - 1),
                    actions=self._length.AddNumber(1),
                )

            @EUDFunc
            def popleft():
                nonlocal jump
                jump << RawTrigger(nextptr=queue)
                RawTrigger(
                    actions=[
                        pop,
                        SetMemory(jump + 4, Add, 72),
                        self._length.AddNumber(-1),
                    ],
                )
                RawTrigger(
                    conditions=Memory(jump + 4, AtLeast, queue + 72 * capacity),
                    actions=SetMemory(jump + 4, SetTo, queue),
                )
                return ret

            self._append = append
            self._popleft = popleft

            PushTriggerScope()
            append(0)
            popleft()
            PopTriggerScope()

        def append(self, value, **kwargs):
            self._append(value, **kwargs)

        def popleft(self, **kwargs):
            return self._popleft(**kwargs)

        def empty(self):
            return self._length == 0

        @property  # FIXME: eudplib code can mutate length
        def length(self):
            return self._length

        def eqattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length == k
            raise AttributeError

        def neattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length != k
            raise AttributeError

        def leattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length <= k
            raise AttributeError

        def ltattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length < k
            raise AttributeError

        def geattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length >= k
            raise AttributeError

        def gtattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length > k
            raise AttributeError

    return _EUDQueue


@cachedfunc
def EUDDeque(capacity):
    """A double-ended queue implemented with a fixed-size variable array."""
    ep_assert(isinstance(capacity, int) and capacity > 0)

    class _EUDDeque:
        def __init__(self):
            ret = EUDVariable()
            pop = EUDVariable(ret, SetTo, 0)
            deque = EUDVArray(capacity)(dest=EPD(pop.getValueAddr()), nextptr=pop.GetVTable())
            append_action = SetMemory(deque + 348, SetTo, 0)
            appendleft_action = SetMemory(deque + 348, SetTo, 0)
            jump, jumpleft = Forward(), Forward()
            self._length = EUDVariable(0)

            @_EUDPredefineParam((EPD(append_action) + 5,))
            @EUDFunc
            def append(value):
                # deque[head] = value
                # head %+ 1
                RawTrigger(
                    actions=[
                        append_action,
                        SetMemory(append_action + 16, Add, 18),
                        SetMemory(jump + 4, Add, 72),
                    ],
                )
                RawTrigger(
                    conditions=Memory(
                        append_action + 16, AtLeast, EPD(deque) + 87 + 18 * capacity
                    ),
                    actions=[
                        SetMemory(append_action + 16, Add, -(18 * capacity)),
                        SetMemory(jump + 4, Add, -(72 * capacity)),
                    ],
                )
                RawTrigger(
                    conditions=self._length.AtMost(capacity - 1),
                    actions=self._length.AddNumber(1),
                )

            @EUDFunc
            def _pop():
                # head %- 1
                # return deque[head]
                nonlocal jump
                retpoint = Forward()
                RawTrigger(
                    conditions=Memory(jump + 4, AtMost, deque),
                    actions=[
                        SetMemory(append_action + 16, Add, 18 * capacity),
                        SetMemory(jump + 4, Add, 72 * capacity),
                    ],
                )
                jump << RawTrigger(
                    nextptr=deque,
                    actions=[
                        SetNextPtr(pop.GetVTable(), retpoint),
                        SetMemory(append_action + 16, Add, -18),
                        SetMemory(jump + 4, Add, -72),
                        self._length.AddNumber(-1),
                    ],
                )
                retpoint << NextTrigger()
                return ret

            @_EUDPredefineParam((EPD(appendleft_action) + 5,))
            @EUDFunc
            def appendleft(value):
                # tail %- 1
                # deque[tail] = value
                RawTrigger(
                    conditions=Memory(appendleft_action + 16, AtMost, EPD(deque) + 87),
                    actions=[
                        SetMemory(appendleft_action + 16, Add, 18 * capacity),
                        SetMemory(jumpleft + 4, Add, 72 * capacity),
                    ],
                )
                RawTrigger(
                    actions=[
                        SetMemory(appendleft_action + 16, Add, -18),
                        SetMemory(jumpleft + 4, Add, -72),
                        appendleft_action,
                    ],
                )
                RawTrigger(
                    conditions=self._length.AtMost(capacity - 1),
                    actions=self._length.AddNumber(1),
                )

            @EUDFunc
            def popleft():
                # ret = deque[tail]
                # tail %+ 1
                # return ret
                nonlocal jumpleft
                wraparound = Forward()
                jumpleft << RawTrigger(
                    nextptr=deque - 72,
                    actions=[
                        SetNextPtr(pop.GetVTable(), wraparound),
                        self._length.AddNumber(-1),
                        SetMemory(appendleft_action + 16, Add, 18),
                        SetMemory(jumpleft + 4, Add, 72),
                    ],
                )
                wraparound << RawTrigger(
                    conditions=Memory(jumpleft + 4, AtLeast, deque + 72 * (capacity - 1)),
                    actions=[
                        SetMemory(appendleft_action + 16, Add, -(18 * capacity)),
                        SetMemory(jumpleft + 4, Add, -(72 * capacity)),
                    ],
                )
                return ret

            self._append = append
            self._appendleft = appendleft
            self._pop = _pop
            self._popleft = popleft

            PushTriggerScope()
            append(0)
            _pop()
            appendleft(0)
            popleft()
            PopTriggerScope()

        def append(self, value, **kwargs):
            self._append(value, **kwargs)

        def pop(self, **kwargs):
            return self._pop(**kwargs)

        def appendleft(self, value, **kwargs):
            self._appendleft(value, **kwargs)

        def popleft(self, **kwargs):
            return self._popleft(**kwargs)

        def empty(self):
            return self._length == 0

        @property  # FIXME: eudplib code can mutate length
        def length(self):
            return self._length

        def eqattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length == k
            raise AttributeError

        def neattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length != k
            raise AttributeError

        def leattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length <= k
            raise AttributeError

        def ltattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length < k
            raise AttributeError

        def geattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length >= k
            raise AttributeError

        def gtattr(self, attr, k):
            if isinstance(attr, str) and attr == "length":
                return self._length > k
            raise AttributeError

    return _EUDDeque
