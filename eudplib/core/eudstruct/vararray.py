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
from ...utils import EPD, ExprProxy, ep_assert, cachedfunc, isUnproxyInstance, ep_assert

from ..variable import EUDVariable, SeqCompute, VProc, IsEUDVariable
from ..variable.eudv import _ProcessDest
from ..variable.vbuf import GetCurrentVariableBuffer, GetCurrentCustomVariableBuffer


@cachedfunc
def EUDVArrayData(size):
    ep_assert(isinstance(size, int))

    class _EUDVArrayData(ConstExpr):
        def __init__(self, initvars, *, dest=0, nextptr=0):
            super().__init__(self)
            ep_assert(
                len(initvars) == size,
                _("{} items expected, got {}").format(size, len(initvars)),
            )
            if dest != 0 or nextptr != 0:
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


_index = EUDVariable()
_goto_getidx = [Forward() for _ in range(32)]
_ret_getidx, _end_getidx = Forward(), Forward()


@cachedfunc
def EUDVArray(size, basetype=None):
    ep_assert(isinstance(size, int))

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

        def get(self, i):
            if IsEUDVariable(i):
                r = self._eudget(i)
            else:
                ep_assert(i < size, _("EUDVArray index out of bounds."))
                if IsEUDVariable(self):
                    r = self._get(i)
                else:
                    r = self._constget(i)

            if self._basetype:
                r = self._basetype.cast(r)
            return r

        def _eudget(self, i):
            global _goto_getidx, _ret_getidx, _end_getidx
            if not _end_getidx.IsSet():
                bt.PushTriggerScope()

                for t in range(31, -1, -1):
                    _goto_getidx[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=[
                            bt.SetMemory(_end_getidx + 4, bt.Add, 72 * (2**t)),
                            bt.SetMemory(_ret_getidx + 16, bt.Add, 18 * (2**t)),
                            bt.SetMemory(_ret_getidx + 48, bt.Add, 18 * (2**t)),
                        ],
                    )
                _end_getidx << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        _ret_getidx << bt.SetDeaths(0, bt.SetTo, 0, 0),
                        bt.SetDeaths(0, bt.SetTo, 0, 0),
                    ],
                )
                bt.PopTriggerScope()

            r = EUDVariable()
            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()

            SeqCompute(
                [
                    (EPD(_end_getidx + 4), bt.SetTo, self),
                    (EPD(_ret_getidx + 16), bt.SetTo, self._epd + 344 // 4),
                    (EPD(_ret_getidx + 48), bt.SetTo, self._epd + 1),
                ]
            )
            bt.RawTrigger(
                nextptr=i.GetVTable(),
                actions=[
                    i.QueueAssignTo(_index),
                    bt.SetNextPtr(i.GetVTable(), _goto_getidx[bits]),
                    bt.SetMemory(_ret_getidx + 20, bt.SetTo, EPD(r.getValueAddr())),
                    bt.SetMemory(_ret_getidx + 52, bt.SetTo, nptr),
                ],
            )

            nptr << bt.NextTrigger()
            return r

        def _get(self, i):
            # This function is hand-optimized

            r = EUDVariable()
            vtproc = Forward()
            nptr = Forward()
            a0, a2 = Forward(), Forward()

            SeqCompute(
                [
                    (EPD(vtproc + 4), bt.SetTo, self + 72 * i),
                    (EPD(a0 + 16), bt.SetTo, self._epd + (18 * i + 344 // 4)),
                    (EPD(a2 + 16), bt.SetTo, self._epd + (18 * i + 1)),
                ]
            )
            vtproc << bt.RawTrigger(
                nextptr=0,
                actions=[
                    a0 << bt.SetDeaths(0, bt.SetTo, EPD(r.getValueAddr()), 0),
                    a2 << bt.SetDeaths(0, bt.SetTo, nptr, 0),
                ],
            )

            nptr << bt.NextTrigger()
            return r

        def _constget(self, i):
            r = EUDVariable()
            nptr = Forward()

            bt.RawTrigger(
                nextptr=self + 72 * i,
                actions=[
                    bt.SetDeaths(
                        self._epd + (18 * i + 344 // 4),
                        bt.SetTo,
                        EPD(r.getValueAddr()),
                        0,
                    ),
                    bt.SetDeaths(self._epd + (18 * i + 1), bt.SetTo, nptr, 0),
                ],
            )

            nptr << bt.NextTrigger()
            return r

        def set(self, i, value):
            if IsConstExpr(self) and IsConstExpr(i):
                if isUnproxyInstance(i, int):
                    ep_assert(i < size, _("EUDVArray index out of bounds."))
                if IsEUDVariable(value):
                    self._consteudset(i, value)
                else:
                    self._constset(i, value)
            else:
                self._set(i, value)

        def _set(self, i, value):
            # This function is hand-optimized

            a0, t = Forward(), Forward()
            SeqCompute(
                [
                    (EPD(a0 + 16), bt.SetTo, self._epd + (18 * i + 348 // 4)),
                    (EPD(a0 + 20), bt.SetTo, value),
                ]
            )
            t << bt.RawTrigger(actions=[a0 << bt.SetDeaths(0, bt.SetTo, 0, 0)])

        def _consteudset(self, i, value):
            VProc(value, [value.QueueAssignTo(self._epd + (18 * i + 348 // 4))])

        def _constset(self, i, value):
            bt.RawTrigger(
                actions=bt.SetDeaths(
                    self._epd + (18 * i + 348 // 4), bt.SetTo, value, 0
                )
            )

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
            raise ut.EPError(_("Can't iterate EUDVArray"))

    return _EUDVArray
