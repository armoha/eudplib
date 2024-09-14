# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from . import modcurpl as cp


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
        for i in ut._rand_lst(range(3)):
            if cs.EUDSwitchCase()(i):
                c.VProc(
                    byte,
                    [byte.SetDest(self._b[i]), self._suboffset.AddNumber(1)],
                )
                cs.EUDBreak()

        if cs.EUDSwitchCase()(3):
            c.VProc(byte, byte.SetDest(self._b[3]))
            self.flushdword()

        cs.EUDEndSwitch()

    @c.EUDMethod
    def flushdword(self):
        """Flush buffer."""
        # mux bytes
        cs.DoActions(c.SetDeaths(cp.CP, c.SetTo, 0, 0))
        if cs.EUDIf()(self._suboffset == 0):
            c.EUDReturn()
        cs.EUDEndIf()

        c.VProc(self._b[0], self._b[0].SetDest(cp.CP))
        for k in ut._rand_lst(range(8, 32)):
            i, j = divmod(k, 8)
            c.RawTrigger(
                conditions=self._b[i].AtLeastX(1, 2**j),
                actions=c.SetDeaths(cp.CP, c.Add, 2**k, 0),
            )
        cs.DoActions(
            *c.AddCurrentPlayer(1),
            self._suboffset.SetNumber(0),
            self._b[0].SetNumber(ut.b2i1(b"\r")),
            self._b[1].SetNumber(ut.b2i1(b"\r")),
            self._b[2].SetNumber(ut.b2i1(b"\r")),
            self._b[3].SetNumber(ut.b2i1(b"\r")),
        )
