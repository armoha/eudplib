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
from math import log2
from .. import core as c
from .. import utils as ut
from .memiof import f_dwread_epd, f_dwwrite_epd, f_dwadd_epd, f_setcurpl2cpcache
from .memiof.inplacecw import iset, cpset
from ..localize import _


class EUDArrayData(c.EUDObject):
    """
    Structure for storing multiple values.
    """

    def __init__(self, arr):
        super().__init__()
        self.dontFlatten = True

        if isinstance(arr, int):
            arrlen = arr
            self._datas = [0] * arrlen
            self._arrlen = arrlen

        else:
            for i, item in enumerate(arr):
                ut.ep_assert(c.IsConstExpr(item), _("Invalid item #{}").format(i))
            self._datas = arr
            self._arrlen = len(arr)

    def GetDataSize(self):
        return self._arrlen * 4

    def WritePayload(self, buf):
        for item in self._datas:
            buf.WriteDword(item)

    # --------

    def GetArraySize(self):
        """Get size of array"""
        return self._arrlen


class EUDArray(ut.ExprProxy):
    def __init__(self, initval=None, *, _from=None):
        if _from is not None:
            dataObj = _from

        else:
            dataObj = EUDArrayData(initval)
            self.length = dataObj._arrlen

        super().__init__(dataObj)
        self._epd = ut.EPD(self)
        self.dontFlatten = True

    def get(self, key):
        return f_dwread_epd(self._epd + key)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, key, item):
        return iset(self._epd, key, c.SetTo, item)

    def __setitem__(self, key, item):
        return self.set(key, item)

    def __iter__(self):
        raise EPError(_("Can't iterate EUDArray"))

    # in-place item operations
    # Total 6 cases = 3 × 2
    # [0, 1, 2] of (self._epd, key) are variable
    #  × val is variable or not
    def iadditem(self, key, val):
        return iset(self._epd, key, c.Add, val)

    # FIXME: add operator for f_dwsubtract_epd
    def isubtractitem(self, key, val):
        return iset(self._epd, key, c.Subtract, val)

    def isubitem(self, key, val):
        if not c.IsEUDVariable(val):
            return iset(self._epd, key, c.Add, -val)
        dst = c.EncodePlayer(c.CurrentPlayer)
        trg = f_setcurpl2cpcache
        if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
            dst = self._epd + key
            trg = c.RawTrigger
            # x - b = -(-x + b) = ~(~x + 1 + b) + 1
            # Run 3 triggers, 10 actions
        elif c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
            c.VProc(
                [self._epd, key],
                [
                    self._epd.QueueAssignTo(ut.EPD(0x6509B0)),
                    key.QueueAddTo(ut.EPD(0x6509B0)),
                ],
            )
        else:
            ev, cn = self._epd, key
            if c.IsEUDVariable(key):
                ev, cn = key, self._epd
            c.VProc(
                ev,
                [
                    c.SetMemory(0x6509B0, c.SetTo, cn),
                    ev.QueueAddTo(ut.EPD(0x6509B0)),
                ],
            )
        c.VProc(
            val,
            [
                c.SetMemoryXEPD(dst, Add, -1, 0x55555555),
                c.SetMemoryXEPD(dst, Add, -1, 0xAAAAAAAA),
                c.SetMemoryEPD(dst, Add, 1),
                val.QueueAddTo(dst),
            ],
        )
        return trg(
            actions=[
                c.SetMemoryXEPD(dst, Add, -1, 0x55555555),
                c.SetMemoryXEPD(dst, Add, -1, 0xAAAAAAAA),
                c.SetMemoryEPD(dst, Add, 1),
            ],
        )

    # defined when val is power of 2
    def imulitem(self, key, val):
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            return f_dwwrite_epd(self._epd + key, 0)
        # val is power of 2
        if val & (val - 1) == 0:
            return self.ilshiftitem(key, int(log2(val)))
        # val is negation of power of 2
        if -val & (-val - 1) == 0:
            pass
        raise AttributeError

    # defined when val is power of 2
    def ifloordivitem(self, key, val):
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            raise ZeroDivisionError
        # val is power of 2
        if val & (val - 1) == 0:
            return self.irshiftitem(key, int(log2(val)))
        # val is negation of power of 2
        if -val & (-val - 1) == 0:
            pass
        raise AttributeError

    # defined when val is power of 2
    def imoditem(self, key, val):
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            raise ZeroDivisionError
        # val is power of 2
        if val & (val - 1) == 0:
            return self.ianditem(key, val - 1)
        raise AttributeError

    # FIXME: merge logic with EUDVariable and VariableBase

    def ilshiftitem(self, key, val):
        if isinstance(val, int):
            n = val
            mask = (1 << (n + 1)) - 1
            dst, trg = cpset(self._epd, key)
            itemw = lambda mod, value, mask: c.SetMemoryXEPD(dst, mod, value, mask)
            return trg(
                actions=[
                    [
                        itemw(c.SetTo, 0, (mask >> 1) << (n + 1)),
                        itemw(c.Add, (mask >> 1) << n, mask << n),
                    ]
                    for n in reversed(range(32 - n))
                ]
                + [itemw(c.SetTo, 0, mask >> 1)]  # lowest n bits
            )
        raise AttributeError

    def irshiftitem(self, key, val):
        if isinstance(val, int):
            n = val
            mask = (1 << (n + 1)) - 1
            dst, trg = cpset(self._epd, key)
            sub = lambda value, mask: c.SetMemoryXEPD(dst, c.Subtract, value, mask)
            return trg(
                actions=[c.SetMemoryXEPD(dst, c.SetTo, 0, mask >> 1)]  # lowest n bits
                + [sub((mask >> 1) << n, mask << n) for n in range(32 - n)]
            )
        raise AttributeError

    def ipowitem(self, key, val):
        raise AttributeError

    def ianditem(self, key, val):
        if not c.IsEUDVariable(val):
            if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
                return c.RawTrigger(
                    actions=SetMemoryXEPD(self._epd + key, c.SetTo, 0, ~val)
                )

            write = c.SetMemoryXEPD(0, c.SetTo, 0, ~val)
            if c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
                c.VProc(
                    [self._epd, key],
                    [
                        self._epd.QueueAssignTo(ut.EPD(write) + 4),
                        key.QueueAddTo(ut.EPD(write) + 4),
                    ],
                )
            else:
                ev, cn = self._epd, key
                if c.IsEUDVariable(key):
                    ev, cn = key, self._epd
                c.VProc(
                    ev,
                    [
                        c.SetMemory(write + 16, c.SetTo, cn),
                        ev.QueueAddTo(ut.EPD(write) + 4),
                    ],
                )
            return c.RawTrigger(actions=write)

        if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
            write = c.SetMemoryXEPD(self._epd + key, c.SetTo, 0, 0)
            c.VProc(val, val.QueueAssignTo(ut.EPD(write)))
        elif c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
            write = c.SetMemoryXEPD(0, c.SetTo, ~0, 0)
            c.VProc(
                [self._epd, key, val],
                [
                    self._epd.QueueAssignTo(ut.EPD(write) + 4),
                    key.QueueAddTo(ut.EPD(write) + 4),
                    val.QueueAssignTo(ut.EPD(write)),
                ],
            )
        else:
            write = c.SetMemoryXEPD(0, c.SetTo, ~0, 0)
            ev, cn = self._epd, key
            if c.IsEUDVariable(key):
                ev, cn = key, self._epd
            c.VProc(
                [ev, val],
                [
                    c.SetMemory(write + 16, c.SetTo, cn),
                    ev.QueueAddTo(ut.EPD(write) + 4),
                    val.QueueAssignTo(ut.EPD(write)),
                ],
            )
        return c.RawTrigger(
            actions=[
                c.SetMemory(write, c.Add, -1, 0x55555555),
                c.SetMemory(write, c.Add, -1, 0xAAAAAAAA),
                write,
            ],
        )

    def ioritem(self, key, val):
        if not c.IsEUDVariable(val):
            if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
                return c.RawTrigger(
                    actions=SetMemoryXEPD(self._epd + key, c.SetTo, ~0, val)
                )

            write = c.SetMemoryXEPD(0, c.SetTo, ~0, val)
            if c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
                c.VProc(
                    [self._epd, key],
                    [
                        self._epd.QueueAssignTo(ut.EPD(write) + 4),
                        key.QueueAddTo(ut.EPD(write) + 4),
                    ],
                )
            else:
                ev, cn = self._epd, key
                if c.IsEUDVariable(key):
                    ev, cn = key, self._epd
                c.VProc(
                    ev,
                    [
                        c.SetMemory(write + 16, c.SetTo, cn),
                        ev.QueueAddTo(ut.EPD(write) + 4),
                    ],
                )
            return c.RawTrigger(actions=write)

        if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
            write = c.SetMemoryXEPD(self._epd + key, c.SetTo, ~0, 0)
            c.VProc(val, val.QueueAssignTo(ut.EPD(write)))
            return c.RawTrigger(actions=write)

        write = c.SetMemoryXEPD(0, c.SetTo, ~0, 0)
        if c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
            c.VProc(
                [self._epd, key, val],
                [
                    self._epd.QueueAssignTo(ut.EPD(write) + 4),
                    key.QueueAddTo(ut.EPD(write) + 4),
                    val.QueueAssignTo(ut.EPD(write)),
                ],
            )
        else:
            ev, cn = self._epd, key
            if c.IsEUDVariable(key):
                ev, cn = key, self._epd
            c.VProc(
                [ev, val],
                [
                    c.SetMemory(write + 16, c.SetTo, cn),
                    ev.QueueAddTo(ut.EPD(write) + 4),
                    val.QueueAssignTo(ut.EPD(write)),
                ],
            )
        return c.RawTrigger(actions=write)

    def ixoritem(self, key, val):
        if not c.IsEUDVariable(val):
            dst, trg = cpset(self._epd, key)
            return trg(
                actions=[
                    c.SetMemoryXEPD(dst, Add, val, 0x55555555),
                    c.SetMemoryXEPD(dst, Add, val, 0xAAAAAAAA),
                ],
            )

        dst = ut.EPD(val.getDestAddr())
        if not (c.IsEUDVariable(self._epd) or c.IsEUDVariable(key)):
            c.VProc(
                val,
                [
                    val.QueueAddTo(self._epd + key),
                    val.SetMask(0x55555555),
                ],
            )
        elif c.IsEUDVariable(self._epd) and c.IsEUDVariable(key):
            c.VProc(
                [self._epd, key, val],
                [
                    self._epd.QueueAssignTo(dst),
                    key.QueueAddTo(dst),
                    val.SetMask(0x55555555),
                    val.SetModifier(c.Add),
                ],
            )
        else:
            ev, cn = self._epd, key
            if c.IsEUDVariable(key):
                ev, cn = key, self._epd
            c.VProc(
                [ev, val],
                [
                    ev.QueueAddTo(dst),
                    val.QueueAddTo(cn),
                    val.SetMask(0x55555555),
                ],
            )
        c.VProc(val, val.SetMask(0xAAAAAAAA))
        # FIXME: restore to previous mask???
        return c.RawTrigger(actions=val.SetMask(0xFFFFFFFF))

    # FIXME: Add operator?
    def iinvert(self, key):
        return self.ixoritem(key, 0xFFFFFFFF)

    def inot(self, key):
        raise AttributeError

    # item comparisons
    def eqitem(self, key, val):
        return c.MemoryEPD(self._epd + key, c.Exactly, val)

    def leitem(self, key, val):
        return c.MemoryEPD(self._epd + key, c.AtMost, val)

    def geitem(self, key, val):
        return c.MemoryEPD(self._epd + key, c.AtLeast, val)

    def neitem(self, key, val):
        return ut.EUDNot(c.MemoryEPD(self._epd + key, c.Exactly, val))

    def ltitem(self, key, val):
        return ut.EUDNot(c.MemoryEPD(self._epd + key, c.AtMost, val))

    def gtitem(self, key, val):
        return ut.EUDNot(c.MemoryEPD(self._epd + key, c.AtLeast, val))
