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

from .. import rawtrigger as bt
from ..allocator import Forward, ConstExpr, IsConstExpr

from ...localize import _
from ..inplacecw import iset, cpset, isub, iand, ior, ixor, ilshift, irshift
from ...utils import EPD, ExprProxy, ep_assert, cachedfunc, isUnproxyInstance, ep_assert

from ..variable import EUDVariable, EUDLightVariable, SeqCompute, VProc, IsEUDVariable
from ..variable.eudv import _ProcessDest
from ..variable.vbuf import GetCurrentVariableBuffer, GetCurrentCustomVariableBuffer


@cachedfunc
def EUDVArrayData(size):
    ep_assert(isinstance(size, int) and size < 2**28, "invalid size")

    class _EUDVArrayData(ConstExpr):
        def __init__(self, initvars, *, dest=0, nextptr=0):
            super().__init__(self)
            ep_assert(
                len(initvars) == size,
                _("{} items expected, got {}").format(size, len(initvars)),
            )
            for i, item in enumerate(initvars):
                ep_assert(IsConstExpr(item), _("Invalid item #{}").format(i))
            if not all(isinstance(x, int) and x == 0 for x in (dest, nextptr)):
                ep_assert(IsConstExpr(nextptr), _("nextptr should be ConstExpr"))
                initvars = [
                    (0xFFFFFFFF, _ProcessDest(dest), initvar, 0x072D0000, nextptr)
                    for initvar in initvars
                ]
            self._initvars = initvars

        def Evaluate(self):
            if all(isinstance(var, tuple) for var in self._initvars):
                evb = GetCurrentCustomVariableBuffer()
            else:
                evb = GetCurrentVariableBuffer()
            if self not in evb._vdict:
                evb.CreateMultipleVarTriggers(self, self._initvars)

            return evb._vdict[self].Evaluate()

    return _EUDVArrayData


_index = EUDLightVariable()


class BitsTrg:
    cache = {}

    def __init__(self, key):
        self._key = key

    def __bool__(self):
        return self._key in BitsTrg.cache

    def __iter__(self):
        if not self:
            BitsTrg.cache[self._key] = {i: Forward() for i in range(28)}
            bt.PushTriggerScope()
            yield BitsTrg.cache[self._key]
            bt.PopTriggerScope()

    def __getitem__(self, index):
        return BitsTrg.cache[self._key][index]

    def __setitem__(self, index, item):
        BitsTrg.cache[self._key][index] = item


@cachedfunc
def EUDVArray(size, basetype=None):
    ep_assert(isinstance(size, int) and size < 2**28, "invalid size")

    class _EUDVArray(ExprProxy):
        def __init__(self, initvars=None, *, dest=0, nextptr=0, _from=None):
            # Initialization from value
            if _from is not None:
                if IsConstExpr(_from):
                    baseobj = _from

                # Initialization by variable reference
                else:
                    baseobj = EUDVariable()
                    baseobj << _from

            else:
                # Int -> interpret as sequence of 0s
                if initvars is None:
                    initvars = [0] * size

                # For python iterables
                baseobj = EUDVArrayData(size)(initvars, dest=dest, nextptr=nextptr)

            super().__init__(baseobj)
            self.dontFlatten = True
            self._epd = EPD(self)
            self._basetype = basetype

        def get(self, i, **kwargs):
            if IsEUDVariable(i):
                r = self._eudget(i, **kwargs)
            else:
                ep_assert(i < size, _("EUDVArray index out of bounds."))
                if IsEUDVariable(self):
                    r = self._get(i, **kwargs)
                else:
                    r = self._constget(i, **kwargs)

            if self._basetype:
                r = self._basetype.cast(r)
            return r

        def _eudget(self, i, **kwargs):
            bitstrg = BitsTrg("varrget")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=[
                            bt.SetMemory(trg["end"] + 4, bt.Add, 72 * (2**t)),
                            bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                            bt.SetMemory(trg["ret"] + 48, bt.Add, 18 * (2**t)),
                        ],
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        trg["ret"] << bt.SetDeaths(0, bt.SetTo, 0, 0),
                        bt.SetDeaths(0, bt.SetTo, 0, 0),
                    ],
                )

            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if not IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["end"] + 4, bt.SetTo, self),
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 86),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, dst),
                        bt.SetMemory(bitstrg["ret"] + 48, bt.SetTo, self._epd + 1),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, nptr),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            else:
                VProc(
                    [self, self._epd],
                    [
                        self.QueueAssignTo(EPD(bitstrg["end"]) + 1),
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 86),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, dst),
                    ],
                )
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 48, bt.SetTo, 1),
                        self._epd.SetDest(EPD(bitstrg["ret"]) + 12),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, nptr),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            nptr << bt.NextTrigger()
            return r

        def _get(self, i, **kwargs):
            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            vtproc = Forward()
            nptr = Forward()
            a0, a2 = Forward(), Forward()

            VProc(
                [self, self._epd],
                [
                    bt.SetMemory(vtproc + 4, bt.SetTo, 72 * i),
                    self.QueueAddTo(EPD(vtproc) + 1),
                    bt.SetMemory(a0 + 16, bt.SetTo, 18 * i + 344 // 4),
                    self._epd.QueueAddTo(EPD(a0) + 4),
                ],
            )
            VProc(
                self._epd,
                [
                    a0 << bt.SetDeaths(0, bt.SetTo, dst, 0),
                    bt.SetMemory(a2 + 16, bt.SetTo, 18 * i + 1),
                    self._epd.SetDest(EPD(a2) + 4),
                ],
            )
            vtproc << bt.RawTrigger(
                nextptr=0,
                actions=[a2 << bt.SetDeaths(0, bt.SetTo, nptr, 0)],
            )

            nptr << bt.NextTrigger()
            return r

        def _constget(self, i, **kwargs):
            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            nptr = Forward()

            bt.RawTrigger(
                nextptr=self + 72 * i,
                actions=[
                    bt.SetDeaths(self._epd + 18 * i + 86, bt.SetTo, dst, 0),
                    bt.SetDeaths(self._epd + 18 * i + 1, bt.SetTo, nptr, 0),
                ],
            )
            nptr << bt.NextTrigger()
            return r

        def set(self, i, val):
            self._set(i, bt.SetTo, val)

        def _set(self, i, modifier, val):
            if not IsEUDVariable(i):
                return iset(self._epd, 18 * i + 348 // 4, modifier, val)
            modifier = bt.EncodeModifier(modifier) << 24

            bitstrg = BitsTrg("varrset")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[trg["ret"] << bt.SetDeaths(0, bt.SetTo, 0, 0)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def fill(self, values, *, assert_expected_values_len=None):
            if assert_expected_values_len:
                ep_assert(len(values) == assert_expected_values_len)

            SeqCompute(
                [
                    (self._epd + (18 * i + 348 // 4), bt.SetTo, value)
                    for i, value in enumerate(values)
                ]
            )

        def __getitem__(self, i):
            return self.get(i)

        def __setitem__(self, i, value):
            self.set(i, value)

        def __iter__(self):
            # FIXME: add EUDVArray iterator
            raise ut.EPError(_("Can't iterate EUDVArray"))

        def iadditem(self, i, val):
            self._set(i, bt.Add, val)

        # FIXME: add operator for Subtract
        def isubtractitem(self, i, val):
            self._set(i, bt.Subtract, val)

        def isubitem(self, i, val):
            if not IsEUDVariable(val):
                return self._set(i, bt.Add, -val)
            if not IsEUDVariable(i):
                return isub(self._epd, 18 * i + 87, val)
            bitstrg = BitsTrg("varrsub")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        bt.SetMemoryX(trg["ret"] + 20, bt.Add, -1, 0x55555555),
                        bt.SetMemoryX(trg["ret"] + 20, bt.Add, -1, 0xAAAAAAAA),
                        bt.SetMemoryEPD(trg["ret"] + 20, bt.Add, 1),
                        trg["ret"] << bt.SetDeaths(0, bt.Add, 0, 0),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        # defined when val is power of 2
        def imulitem(self, i, val):
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                return self.set(i, 0)
            # val is power of 2
            if val & (val - 1) == 0:
                return self.ilshiftitem(i, int(log2(val)))
            # val is negation of power of 2
            if -val & (-val - 1) == 0:
                pass
            raise AttributeError

        # defined when val is power of 2
        def ifloordivitem(self, i, val):
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                raise ZeroDivisionError
            # val is power of 2
            if val & (val - 1) == 0:
                return self.irshiftitem(i, int(log2(val)))
            # val is negation of power of 2
            if -val & (-val - 1) == 0:
                pass
            raise AttributeError

        # defined when val is power of 2
        def imoditem(self, i, val):
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                raise ZeroDivisionError
            # val is power of 2
            if val & (val - 1) == 0:
                return self.ianditem(i, val - 1)
            raise AttributeError

        # FIXME: merge logic with EUDVariable and VariableBase

        def ilshiftitem(self, i, n):
            if not isinstance(n, int):
                raise AttributeError
            if not IsEUDVariable(i):
                return ilshift(self._epd, 18 * i + 87, n)
            if n == 0:
                return
            bitstrg = BitsTrg(f"varrlshift{n}")
            cp = bt.EncodePlayer(bt.CurrentPlayer)
            for trg in bitstrg:
                trg["end"] = Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )
                itemw = lambda mod, value, mask: bt.SetMemoryXEPD(cp, mod, value, mask)
                trg["end"] << bt.RawTrigger(
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        [
                            itemw(bt.SetTo, 0, (mask >> 1) << (k + 1)),
                            itemw(bt.Add, (mask >> 1) << k, mask << k),
                        ]
                        for k in reversed(range(32 - n))
                    ]
                    + [
                        itemw(bt.SetTo, 0, mask >> 1),
                        GetCPCache().SetDest(EPD(0x6509B0)),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def irshiftitem(self, i, n):
            if not isinstance(n, int):
                raise AttributeError
            if not IsEUDVariable(i):
                return irshift(self._epd, 18 * i + 87, n)
            if n == 0:
                return
            bitstrg = BitsTrg(f"varrrshift{n}")
            cp = bt.EncodePlayer(bt.CurrentPlayer)
            for trg in bitstrg:
                trg["end"] = Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )
                sub = lambda value, mask: bt.SetMemoryXEPD(cp, bt.Subtract, value, mask)
                trg["end"] << bt.RawTrigger(
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        bt.SetMemoryXEPD(cp, bt.SetTo, 0, mask >> 1),
                        GetCPCache().SetDest(EPD(0x6509B0)),
                    ]
                    + [sub((mask >> 1) << k, mask << k) for k in range(32 - n)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ipowitem(self, i, val):
            if isinstance(val, int) and val == 1:
                return
            raise AttributeError

        def ianditem(self, i, val):
            if not IsEUDVariable(i):
                return iand(self._epd, 18 * i + 87, val)
            bitstrg = BitsTrg("varrand")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        bt.SetMemoryX(trg["ret"], bt.Add, -1, 0x55555555),
                        bt.SetMemoryX(trg["ret"], bt.Add, -1, 0xAAAAAAAA),
                        trg["ret"] << bt.SetMemoryXEPD(0, bt.SetTo, 0, 0),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ioritem(self, i, val):
            if not IsEUDVariable(i):
                return ior(self._epd, 18 * i + 87, val)
            bitstrg = BitsTrg("varror")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[trg["ret"] << bt.SetMemoryXEPD(0, bt.SetTo, ~0, 0)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ixoritem(self, i, val):
            from ..curpl import GetCPCache

            if not IsEUDVariable(i):
                return ixor(self._epd, 18 * i + 87, val)
            bitstrg = BitsTrg("varrxor")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        trg["ret"]
                        << bt.SetDeathsX(bt.CurrentPlayer, bt.Add, 0, 0x55555555),
                        bt.SetDeathsX(bt.CurrentPlayer, bt.Add, 0, 0xAAAAAAAA),
                        GetCPCache().SetDest(EPD(0x6509B0)),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr, trg1, trg2 = Forward(), Forward(), Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                trg1 << bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), trg2),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
                trg2 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        val.SetDest(EPD(bitstrg["ret"]) + 13),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            elif IsEUDVariable(val):
                trg1 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), trg2),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
                trg2 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        val.SetDest(EPD(bitstrg["ret"]) + 13),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, val),
                        i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        # FIXME: Add operator?
        def iinvertitem(self, i):
            return self.ixoritem(i, 0xFFFFFFFF)

        def inotitem(self, i):
            raise AttributeError

        # item comparisons
        def eqitem(self, i, val):
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.Exactly, val)
            raise AttributeError

        def neitem(self, i, val):
            if not IsEUDVariable(i):
                from ...eudlib.utilf import EUDNot

                return EUDNot(bt.MemoryEPD(self._epd + (18 * i + 87), bt.Exactly, val))
            raise AttributeError

        def leitem(self, i, val):
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtMost, val)
            raise AttributeError

        def geitem(self, i, val):
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtLeast, val)
            raise AttributeError

        def ltitem(self, i, val):
            if not IsEUDVariable(i):
                from ...eudlib.utilf import EUDNot

                return EUDNot(bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtLeast, val))
            raise AttributeError

        def gtitem(self, i, val):
            if not IsEUDVariable(i):
                from ...eudlib.utilf import EUDNot

                return EUDNot(bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtMost, val))
            raise AttributeError

    return _EUDVArray
