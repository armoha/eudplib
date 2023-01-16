#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..memiof import f_dwread_epd


@c.EUDFunc
def f_getgametick():
    """Get current game tick value."""

    gametick_cache = c.EUDVariable()
    _gametick_cond = c.Forward()

    if cs.EUDIfNot()([_gametick_cond << c.Memory(0x57F23C, c.Exactly, 0)]):
        c.SetVariables(gametick_cache, f_dwread_epd(ut.EPD(0x57F23C)))
        cs.DoActions(c.SetMemory(_gametick_cond + 8, c.SetTo, gametick_cache))
    cs.EUDEndIf()

    return gametick_cache
