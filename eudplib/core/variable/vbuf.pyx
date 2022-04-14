#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
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
'''

from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.stdint cimport uint32_t, uint8_t
from libc.string cimport memset

from ..eudobj import EUDObject
from ... import utils as ut
from ..allocator import RegisterCreatePayloadCallback
from .. import rawtrigger as bt
from collections import deque


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
        cdef size_t i, heads, heade
        cdef size_t olen = 2408 + 72 * (len(self._initvals) - 1)
        cdef uint8_t * output = <uint8_t*> PyMem_Malloc(olen)
        memset(output, 0, olen)
        cdef uint32_t iv2

        for i in range(len(self._initvals)):
            # 'preserve rawtrigger'
            ( < uint32_t*>(output + 72 * i + 328))[0] = 0xFFFFFFFF
            ( < uint32_t*>(output + 72 * i + 352))[0] = 0x072D0000
            ( < uint32_t*>(output + 72 * i + 356))[0] = 0x43530000
            ( < uint32_t*>(output + 72 * i + 2376))[0] = 4

        heads = 0
        for i, initval in enumerate(self._initvals):
            heade = 72 * i + 348
            if initval == 0:
                continue
            elif isinstance(initval, int):
                iv2 = initval & 0xFFFFFFFF
                (<uint32_t*>(output + heade))[0] = iv2
                continue
            emitbuffer.WriteBytes(output[heads:heade])
            emitbuffer.WriteDword(initval)
            heads = heade + 4

        emitbuffer.WriteBytes(output[heads:olen])
        PyMem_Free(output)


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
        cdef size_t i, heads, heade
        cdef size_t olen = 2408 + 72 * (len(self._actnptr_pairs) + len(self._5acts) - 1)
        cdef uint8_t * output = <uint8_t*> PyMem_Malloc(olen)
        memset(output, 0, olen)
        cdef uint32_t iv2

        for i in range(len(self._actnptr_pairs) + len(self._5acts)):
            # 'preserve rawtrigger'
            ( < uint32_t*>(output + 72 * i + 328))[0] = 0xFFFFFFFF
            ( < uint32_t*>(output + 72 * i + 352))[0] = 0x072D0000
            ( < uint32_t*>(output + 72 * i + 356))[0] = 0x43530000
            ( < uint32_t*>(output + 72 * i + 2376))[0] = 4

        heads = 0

        for i, nptr in enumerate(self._5nptrs):
            heade = 72 * i + 4
            if nptr == 0:
                continue
            elif isinstance(nptr, int):
                iv2 = nptr & 0xFFFFFFFF
                (<uint32_t*>(output + heade))[0] = iv2
                continue
            emitbuffer.WriteBytes(output[heads:heade])
            emitbuffer.WriteDword(nptr)
            heads = heade + 4

        # bitmask, player, initval, modifier, nptr
        offsets = (328, 344, 348, 352, 364)
        initials = (0xFFFFFFFF, 0, 0, 0x072D0000, 0)
        for i, initvals in enumerate(self._actnptr_pairs):
            for initval, offset, initial in zip(initvals, offsets, initials):
                heade = 72 * i + offset
                if initval == initial:
                    continue
                elif isinstance(initval, int):
                    iv2 = initval & 0xFFFFFFFF
                    (<uint32_t*>(output + heade))[0] = iv2
                    continue
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(initval)
                heads = heade + 4

        for initvals in self._5acts:
            for initval, offset, initial in zip(initvals, offsets[:4], initials[:4]):
                heade = 72 * i + offset
                if initval == initial:
                    continue
                elif isinstance(initval, int):
                    iv2 = initval & 0xFFFFFFFF
                    (<uint32_t*>(output + heade))[0] = iv2
                    continue
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(initval)
                heads = heade + 4
            i += 1

        emitbuffer.WriteBytes(output[heads:olen])
        PyMem_Free(output)


_ecvb = None


def RegisterNewCustomVariableBuffer():
    global _ecvb
    _ecvb = EUDCustomVarBuffer()


def GetCurrentCustomVariableBuffer():
    return _ecvb


RegisterCreatePayloadCallback(RegisterNewCustomVariableBuffer)
