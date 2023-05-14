#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Any

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut

_EUDVArray8: Any = c.EUDVArray(8)  # FIXME : Unsupported dynamic base class


class PVariable(_EUDVArray8):
    def _casteudset(self, index: c.EUDVariable, value: c.EUDVariable) -> None:
        nptr = c.Forward()
        c.VProc(
            self._epd,
            [
                value.SetDest(348 // 4),
                self._epd.QueueAddTo(ut.EPD(value.getDestAddr())),
                c.SetMemory(value._varact + 24, c.SetTo, 0x072D0000),
                c.SetNextPtr(value.GetVTable(), nptr),
            ],
        )
        for k in range(3):
            c.RawTrigger(
                conditions=index.AtLeastX(1, 2**k),
                actions=value.AddDest(18 * (2**k)),
            )
        c.SetNextTrigger(value.GetVTable())
        nptr << c.NextTrigger()

    def _pveudset(self, index: c.EUDVariable, value: c.EUDVariable) -> None:
        nptr = c.Forward()
        cs.DoActions(
            value.SetDest(self._epd + 348 // 4),
            c.SetMemory(value._varact + 24, c.SetTo, 0x072D0000),
            c.SetNextPtr(value.GetVTable(), nptr),
        )
        for k in range(3):
            c.RawTrigger(
                conditions=index.AtLeastX(1, 2**k),
                actions=value.AddDest(18 * (2**k)),
            )
        c.SetNextTrigger(value.GetVTable())
        nptr << c.NextTrigger()

    def __setitem__(self, index, value) -> None:
        index = c.EncodePlayer(index)
        if not c.IsEUDVariable(index):
            return self.set(index, value)
        if c.IsConstExpr(self):
            if c.IsEUDVariable(value):
                self._pveudset(index, value)
            else:
                a0 = c.Forward()
                cs.DoActions(
                    c.SetMemory(a0 + 16, c.SetTo, self._epd + 348 // 4)
                )
                for k in range(2, -1, -1):
                    c.RawTrigger(
                        conditions=index.AtLeastX(1, 2**k),
                        actions=c.SetMemory(a0 + 16, c.Add, 18 * (2**k)),
                    )
                c.RawTrigger(actions=[a0 << c.SetDeaths(0, c.SetTo, value, 0)])
        elif c.IsEUDVariable(value):
            self._casteudset(index, value)
        else:
            a0 = c.Forward()
            c.VProc(
                self._epd,
                [
                    c.SetMemory(a0 + 16, c.SetTo, 348 // 4),
                    self._epd.QueueAddTo(ut.EPD(a0 + 16)),
                ],
            )
            for k in range(3):
                c.RawTrigger(
                    conditions=index.AtLeastX(1, 2**k),
                    actions=c.SetMemory(a0 + 16, c.Add, 18 * (2**k)),
                )
            c.RawTrigger(actions=[a0 << c.SetDeaths(0, c.SetTo, value, 0)])

    def __getitem__(self, i):
        i = c.EncodePlayer(i)
        return super().__getitem__(i)
