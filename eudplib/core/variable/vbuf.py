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

from ..eudobj import EUDObject
from ... import utils as ut
from ..allocator import RegisterCreatePayloadCallback
from .. import rawtrigger as bt


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

    def CreateVarTrigger(
        self, v, initval, modifier=bt.SetTo, value=None, bitmask=None, /
    ):
        ret = self + (72 * len(self._initvals))
        if value is None:
            initval, value = 0, initval
        modifier = bt.EncodeModifier(modifier)
        if bitmask is None:
            bitmask = 0xFFFFFFFF
        self._initvals.append((initval, modifier, value, bitmask))
        self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + (72 * len(self._initvals))
        for initval in initvals:
            # initval: value | (dest, modifier, value, mask)
            if isinstance(initval, tuple) and len(initval) == 4:
                player, modifier, value, bitmask = initval
                modifier = bt.EncodeModifier(modifier)
                self._initvals.append((player, modifier, value, bitmask))
            else:
                modifier = bt.EncodeModifier(bt.SetTo)
                self._initvals.append((0, modifier, initval, 0xFFFFFFFF))
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2408 + 72 * (len(self._initvals) - 1)

    def CollectDependency(self, emitbuffer):
        for initvals in self._initvals:
            for initval in initvals:
                if (initval is not None) and type(initval) is not int:
                    emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        output = bytearray(2408 + 72 * (len(self._initvals) - 1))

        for i in range(len(self._initvals)):
            # 'preserve rawtrigger'
            output[72 * i + 328 : 72 * i + 332] = b"\xFF\xFF\xFF\xFF"
            output[72 * i + 352 : 72 * i + 356] = b"\0\0\x2D\x07"
            output[72 * i + 356 : 72 * i + 360] = b"\0\0SC"
            output[72 * i + 2376 : 72 * i + 2380] = b"\x04\0\0\0"

        heads = 0
        for i, initvals in enumerate(self._initvals):
            player, modifier, initval, bitmask = initvals
            heade = 72 * i + 328
            if bitmask == 0xFFFFFFFF:
                pass
            elif isinstance(bitmask, int):
                output[heade : heade + 4] = ut.i2b4(bitmask)
            else:
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(bitmask)
                heads = heade + 4

            heade += 16
            if player == 0:
                pass
            elif isinstance(player, int):
                output[heade : heade + 4] = ut.i2b4(player)
            else:
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(player)
                heads = heade + 4

            heade += 4
            if initval == 0:
                pass
            elif isinstance(initval, int):
                output[heade : heade + 4] = ut.i2b4(initval)
            else:
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(initval)
                heads = heade + 4

            heade += 4
            if modifier == 7:  # SetTo
                pass
            elif isinstance(modifier, int):
                mf2 = 0x2D0000 + (modifier << 24)
                output[heade : heade + 4] = ut.i2b4(mf2)
            else:
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteWord(0)
                emitbuffer.WriteByte(0x2D)
                emitbuffer.WriteByte(modifier)
                heads = heade + 4

        emitbuffer.WriteBytes(output[heads:])


_evb = None


def RegisterNewVariableBuffer():
    global _evb
    _evb = EUDVarBuffer()


def GetCurrentVariableBuffer():
    return _evb


RegisterCreatePayloadCallback(RegisterNewVariableBuffer)
