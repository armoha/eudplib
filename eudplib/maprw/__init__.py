#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .injector.apply_injector import PRT_SkipPayloadRelocator
from .injector.mainloop import EUDDoEvents, EUDOnStart
from .inlinecode.ilcprocesstrig import PRT_SetInliningRate
from .loadmap import LoadMap
from .mpqadd import MPQAddFile, MPQAddWave, MPQCheckFile
from .savemap import SaveMap

__all__ = [
    "PRT_SkipPayloadRelocator",
    "EUDDoEvents",
    "EUDOnStart",
    "PRT_SetInliningRate",
    "LoadMap",
    "MPQAddFile",
    "MPQAddWave",
    "MPQCheckFile",
    "SaveMap",
]
