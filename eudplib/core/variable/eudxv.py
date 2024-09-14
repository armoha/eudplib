#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing_extensions import Self

from .. import rawtrigger as bt
from ..allocator import ConstExpr
from .eudv import EUDVariable, process_dest
from .vbuf import get_current_custom_varbuffer


# Unused variable don't need to be allocated.
class XVariableTriggerForward(ConstExpr):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(self, initval) -> None:
        super().__init__()
        self._initval = initval

    def Evaluate(self):  # noqa: N802
        evb = get_current_custom_varbuffer()
        try:
            return evb._vdict[self].Evaluate()
        except KeyError:
            vt = evb.create_vartrigger(self, self._initval)
            return vt.Evaluate()


class EUDXVariable(EUDVariable):
    __slots__ = ()

    def __init__(self, epd, modtype, initval, mask=0xFFFFFFFF, /, *, nextptr=0):
        dest = process_dest(epd)
        modifier = ((bt.EncodeModifier(modtype) & 0xFF) << 24) + 0x2D0000
        args = (mask, dest, initval, modifier, nextptr)

        self._vartrigger = XVariableTriggerForward(args)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False
