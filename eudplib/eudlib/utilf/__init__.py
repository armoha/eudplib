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

from .logic import EUDAnd, EUDOr, EUDNot

from .userpl import (
    f_getuserplayerid,
    IsUserCP,
    DisplayTextAll,
    PlayWAVAll,
    MinimapPingAll,
    CenterViewAll,
    SetMissionObjectivesAll,
    TalkingPortraitAll,
)

from .gametick import f_getgametick

from .random import f_getseed, f_srand, f_rand, f_dwrand, f_randomize

from .mempatch import f_dwpatch_epd, f_blockpatch_epd, f_unpatchall

from .pexist import f_playerexist, EUDLoopPlayer, EUDPlayerLoop, EUDEndPlayerLoop

from .listloop import (
    EUDLoopList,
    EUDLoopUnit,
    EUDLoopUnit2,
    EUDLoopNewUnit,
    EUDLoopPlayerUnit,
    EUDLoopSprite,
    EUDLoopBullet,
    EUDLoopTrigger,
)

from .binsearch import EUDBinaryMin, EUDBinaryMax
