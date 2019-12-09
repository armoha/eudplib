#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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

from eudplib import core as c, ctrlstru as cs, utils as ut


class CPByteWriter:
    """Write byte by byte"""

    def __init__(self):
        self._suboffset = c.EUDLightVariable()
        self._b = [c.EUDVariable(ut.b2i1(b"\r"))] + [
            c.EUDLightVariable(ut.b2i1(b"\r")) for _ in range(3)
        ]

    @c.EUDMethod
    def writebyte(self, byte):
        """Write byte to current position.

        Write a byte to current position of EUDByteWriter. Writer will advance
        by 1 byte.

        .. note::
            Bytes could be buffered before written to memory. After you
            finished using writebytes, you must call `flushdword` to flush the
            buffer.
        """
        cs.EUDSwitch(self._suboffset)
        for i in ut.RandList(range(3)):
            if cs.EUDSwitchCase()(i):
                c.VProc(byte, [byte.SetDest(self._b[i]), self._suboffset.AddNumber(1)])
                cs.EUDBreak()

        if cs.EUDSwitchCase()(3):
            c.VProc(byte, byte.SetDest(self._b[3]))
            self.flushdword()

        cs.EUDEndSwitch()

    @c.EUDMethod
    def flushdword(self):
        """Flush buffer."""
        # mux bytes
        cs.DoActions(c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0))
        if cs.EUDIf()(self._suboffset == 0):
            c.EUDReturn()
        cs.EUDEndIf()

        c.VProc(self._b[0], self._b[0].SetDest(c.EncodePlayer(c.CurrentPlayer)))
        for k in ut.RandList(range(8, 32)):
            i, j = divmod(k, 8)
            c.RawTrigger(
                conditions=self._b[i].AtLeastX(1, 2 ** j),
                actions=c.SetDeaths(c.CurrentPlayer, c.Add, 2 ** k, 0),
            )
        cs.DoActions(
            c.AddCurrentPlayer(1),
            self._suboffset.SetNumber(0),
            [self._b[i].SetNumber(ut.b2i1(b"\r")) for i in range(4)],
        )
