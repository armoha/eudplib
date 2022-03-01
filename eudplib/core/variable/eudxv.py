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
    def __init__(self, _initval=0, modifier=None, /, initval=None, mask=None):
        # value (positional)
        if modifier is None and initval is None and mask is None:
            args = (0, bt.SetTo, _initval, ~0)
        # value (keyword)
        elif modifier is None and mask is None:
            args = (0, bt.SetTo, initval, ~0)
        # value, bitmask (positional)
        elif initval is None and mask is None:
            args = (0, bt.SetTo, _initval, modifier)
        # value, bitmask (keyword)
        elif modifier is None and initval is None:
            args = (0, bt.SetTo, _initval, mask)
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
            args = (_ProcessDest(_initval), modifier, initval, mask)

        self._vartrigger = VariableTriggerForward(*args)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False
