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

from collections import deque

from ... import utils as ut
from .. import rawtrigger as bt
from ..allocator import RegisterCreatePayloadCallback
from ..eudobj import EUDObject


class EUDVarBuffer(EUDObject):
    """Variable buffer

    72 bytes per variable.
    """

    def __init__(self):
        super().__init__()

        self._vdict = {}
        self._initvals = []

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, initval):
        ret = self + (72 * len(self._initvals))
        self._initvals.append(initval)
        self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + (72 * len(self._initvals))
        self._initvals.extend(initvals)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2408 + 72 * (len(self._initvals) - 1)

    def CollectDependency(self, emitbuffer):
        for initval in self._initvals:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteSpace(4)

        for _ in range(4):
            emitbuffer.WriteDword(0)  # nextptr
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(52)

        emitbuffer.WriteDword(0)  # nextptr
        emitbuffer.WriteSpace(15)
        emitbuffer.WriteByte(0)  # nocond
        emitbuffer.WriteSpace(16)

        output = bytearray(72 * len(self._initvals))

        for i in range(len(self._initvals)):
            # 'preserve rawtrigger'
            output[72 * i : 72 * i + 4] = b"\xFF\xFF\xFF\xFF"
            output[72 * i + 24 : 72 * i + 28] = b"\0\0\x2D\x07"
            output[72 * i + 28 : 72 * i + 32] = b"\0\0SC"
            output[72 * i + 32 : 72 * i + 36] = b"\x04\0\0\0"

        heads = 0
        for i, initval in enumerate(self._initvals):
            heade = 72 * i + 20
            if initval == 0:
                continue
            elif isinstance(initval, int):
                output[heade : heade + 4] = ut.i2b4(initval)
                continue
            emitbuffer.WriteBytes(output[heads:heade])
            emitbuffer.WriteDword(initval)
            heads = 72 * i + 24

        emitbuffer.WriteBytes(output[heads:])

        emitbuffer.WriteSpace(32)
        emitbuffer.WriteDword(4)  # flags
        emitbuffer.WriteSpace(27)
        emitbuffer.WriteByte(0)  # currentAction

        for _ in range(27):
            emitbuffer.WriteSpace(40)
            emitbuffer.WriteDword(4)  # flags
            emitbuffer.WriteSpace(27)
            emitbuffer.WriteByte(0)  # currentAction


_evb = None


def RegisterNewVariableBuffer():
    global _evb
    _evb = EUDVarBuffer()


def GetCurrentVariableBuffer():
    return _evb


RegisterCreatePayloadCallback(RegisterNewVariableBuffer)


class EUDCustomVarBuffer(EUDObject):
    """Customizable Variable buffer

    72 bytes per variable.
    """

    def __init__(self):
        super().__init__()

        self._vdict = {}
        self._5nptrs = deque([], maxlen=5)
        self._actnptr_pairs = []
        self._5acts = deque([], maxlen=5)

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, initval):
        # bitmask, player, #, modifier, nptr
        ret = self + 72 * (len(self._actnptr_pairs) + len(self._5acts))
        if len(self._5acts) == 5:
            act = self._5acts.popleft()
            act.append(initval[4])
            self._actnptr_pairs.append(act)
        else:
            self._5nptrs.append(initval[4])
        self._5acts.append(deque(initval[0:4], maxlen=5))
        if v is not None:
            self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + 72 * (len(self._actnptr_pairs) + len(self._5acts))
        for initval in initvals:
            self.CreateVarTrigger(None, initval)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2408 + 72 * (len(self._actnptr_pairs) + len(self._5acts) - 1)

    def CollectDependency(self, emitbuffer):
        for initval in self._5nptrs:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)
        for initvals in self._actnptr_pairs:
            for initval in initvals:
                if type(initval) is not int:
                    emitbuffer.WriteDword(initval)
        for initvals in self._5acts:
            for initval in initvals:
                if type(initval) is not int:
                    emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        output = bytearray(72 * (len(self._actnptr_pairs) + len(self._5acts)))

        emitbuffer.WriteSpace(4)

        for i in range(5):
            try:
                emitbuffer.WriteDword(self._5nptrs[i])  # nextptr
            except IndexError:
                emitbuffer.WriteDword(0)
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            if i < 4:
                emitbuffer.WriteSpace(52)
            else:
                emitbuffer.WriteSpace(16)

        for i in range(len(self._actnptr_pairs) + len(self._5acts)):
            # 'preserve rawtrigger'
            output[72 * i : 72 * i + 4] = b"\xFF\xFF\xFF\xFF"
            output[72 * i + 24 : 72 * i + 28] = b"\0\0\x2D\x07"
            output[72 * i + 28 : 72 * i + 32] = b"\0\0SC"
            output[72 * i + 32 : 72 * i + 36] = b"\x04\0\0\0"

        heads = 0

        from itertools import chain

        # bitmask, player, initval, modifier, nptr
        offsets = (0, 16, 20, 24, 36)
        initials = (0xFFFFFFFF, 0, 0, 0x072D0000, 0)
        for i, initvals in enumerate(chain(self._actnptr_pairs, self._5acts)):
            for initval, offset, initial in zip(initvals, offsets, initials):
                heade = 72 * i + offset
                if initval == initial:
                    continue
                elif isinstance(initval, int):
                    output[heade : heade + 4] = ut.i2b4(initval)
                    continue
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(initval)
                heads = 72 * i + offset + 4

        emitbuffer.WriteBytes(output[heads:])

        emitbuffer.WriteSpace(32)
        emitbuffer.WriteDword(4)  # flags
        emitbuffer.WriteSpace(27)
        emitbuffer.WriteByte(0)  # currentAction

        for _ in range(27):
            emitbuffer.WriteSpace(40)
            emitbuffer.WriteDword(4)  # flags
            emitbuffer.WriteSpace(27)
            emitbuffer.WriteByte(0)  # currentAction


_ecvb = None


def RegisterNewCustomVariableBuffer():
    global _ecvb
    _ecvb = EUDCustomVarBuffer()


def GetCurrentCustomVariableBuffer():
    return _ecvb


RegisterCreatePayloadCallback(RegisterNewCustomVariableBuffer)
