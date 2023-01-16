#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ...utils import EPD, EPError
from .. import rawtrigger as bt
from .eudv import EUDVariable, VariableTriggerForward, _ProcessDest


class EUDXVariable(EUDVariable):
    def __init__(self, _initval=0, modifier=None, /, initval=None, mask=None, *, nextptr=0):
        # bitmask, player, #, modifier, nextptr
        # value (positional)
        if modifier is None and initval is None and mask is None:
            args = (0xFFFFFFFF, 0, _initval, 0x072D0000, nextptr)
        # value (keyword)
        elif modifier is None and mask is None:
            args = (0xFFFFFFFF, _ProcessDest(_initval), initval, 0x072D0000, nextptr)
        # value, bitmask (positional)
        elif initval is None and mask is None:
            args = (modifier, 0, _initval, 0x072D0000, nextptr)
        # value, bitmask (keyword)
        elif modifier is None and initval is None:
            args = (mask, 0, _initval, 0x072D0000, nextptr)
        # value, bitmask, mask=bitmask (mixed)
        elif initval is None:
            raise ut.EPError(
                "Ambiguous bitmask. Use EUDXVariable(initval, mask) or EUDXVariable(player, modifier, initval, mask)"
            )
        # value, initval=value, mask=bitmask (mixed)
        # 3 positional args or value, modifier, initval=value
        elif modifier is None or mask is None:
            raise ut.EPError(
                "Ambiguous initval. Use EUDXVariable(initval, mask) or EUDXVariable(player, modifier, initval, mask)"
            )
        else:
            if mask is None:
                mask = 0xFFFFFFFF
            modifier = ((bt.EncodeModifier(modifier) & 0xFF) << 24) + 0x2D0000
            args = (mask, _ProcessDest(_initval), initval, modifier, nextptr)

        self._vartrigger = VariableTriggerForward(args)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False
