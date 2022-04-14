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

from .. import rawtrigger as bt
from ...utils import EPD, EPError
from .eudv import EUDVariable, VariableTriggerForward, _ProcessDest


class EUDXVariable(EUDVariable):
    def __init__(
        self, _initval=0, modifier=None, /, initval=None, mask=None, *, nextptr=0
    ):
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
