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

from ... import core as c
from ... import ctrlstru as cs

from . import dwepdio as dwm, modcurpl as cp
from ...utils import EPD


class EUDByteStream:
    """Read and Write byte by byte."""

    def __init__(self):
        self._suboffset = c.EUDVariable()
        self._offset = c.EUDVariable()

    # -------

    def seekepd(self, epdoffset):
        """Seek EUDByteStream to specific epd player address"""
        if c.IsEUDVariable(epdoffset):
            return c.VProc(
                epdoffset,
                [epdoffset.QueueAssignTo(self._offset), self._suboffset.SetNumber(0)],
            )
        else:
            return c.RawTrigger(
                actions=[
                    self._offset.SetNumber(epdoffset),
                    self._suboffset.SetNumber(0),
                ]
            )

    @c.EUDMethod
    def seekoffset(self, offset):
        """Seek EUDByteStream to specific address"""
        # convert offset to epd offset & suboffset
        q, r = c.f_div(offset, 4)
        c.VProc(
            [q, r],
            [
                self._offset.SetNumber(-0x58A364 // 4),
                q.QueueAddTo(self._offset),
                r.SetDest(self._suboffset),
            ],
        )

    # -------

    @c.EUDMethod
    def readbyte(self):
        """Read byte from current address. ByteStream will advance by 1 bytes.

        :returns: Read byte
        """
        case = [c.Forward() for _ in range(5)]
        ret = c.EUDVariable()

        c.VProc(self._offset, [ret.SetNumber(0), self._offset.SetDest(EPD(0x6509B0))])

        for i in range(3):
            case[i] << c.NextTrigger()
            cs.EUDJumpIfNot(self._suboffset.Exactly(i), case[i + 1])
            for j in range(7, -1, -1):
                c.RawTrigger(
                    conditions=c.DeathsX(
                        c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** (j + 8 * i)
                    ),
                    actions=ret.AddNumber(2 ** j),
                )
            c.RawTrigger(nextptr=case[-1], actions=self._suboffset.AddNumber(1))

        # suboffset == 3
        case[3] << c.NextTrigger()

        for i in range(7, -1, -1):
            c.RawTrigger(
                conditions=[c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** (i + 24))],
                actions=ret.AddNumber(2 ** i),
            )
        cs.DoActions([self._offset.AddNumber(1), self._suboffset.SetNumber(0)])

        case[-1] << c.NextTrigger()
        cp.f_setcurpl2cpcache()
        return ret

    @c.EUDMethod
    def writebyte(self, byte):
        """Write byte to current position.

        Write a byte to current position of EUDByteStream.
        ByteStream will advance by 1 byte.
        """
        _dw = c.Forward()

        cs.EUDSwitch(self._suboffset)
        if cs.EUDSwitchCase()(0):
            cs.DoActions(
                [
                    c.SetMemoryXEPD(self._offset, c.SetTo, byte, 0xFF),
                    self._suboffset.AddNumber(1),
                ]
            )
            c.EUDReturn()

        for i in range(1, 4):
            if cs.EUDSwitchCase()(i):
                cs.DoActions(
                    [
                        c.SetMemory(_dw, c.SetTo, 0xFF << (8 * i)),
                        c.SetMemory(_dw + 20, c.SetTo, 0),
                    ]
                    + [
                        self._suboffset.AddNumber(1)
                        if i < 3
                        else self._suboffset.SetNumber(0)
                    ]
                )
                for j in range(7, -1, -1):
                    c.RawTrigger(
                        conditions=byte.AtLeastX(1, 2 ** j),
                        actions=c.SetMemory(_dw + 20, c.Add, 2 ** (j + i * 8)),
                    )
                cs.EUDBreak()

        cs.EUDEndSwitch()

        cs.DoActions([_dw << c.SetMemoryXEPD(self._offset, c.SetTo, 0, 0xFF00)])
        c.RawTrigger(
            conditions=self._suboffset.Exactly(0), actions=self._offset.AddNumber(1)
        )

    @classmethod
    def flushdword(cls):
        pass


EUDByteReader, EUDByteWriter = EUDByteStream, EUDByteStream
