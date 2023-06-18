#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
from ...core import Db, SetMemory, SetTo
from ...ctrlstru import DoActions
from ...utils import EPD
from ..memiof import f_epdread_epd, f_repmovsd_epd
from .mempatch import f_dwpatch_epd

_data = []


def _add_datadumper(inputData, outOffsets, flags):
    _data.append((inputData, outOffsets, flags))


def _f_datadumper():
    for inputData, outOffsets, flags in _data:
        if len(outOffsets) == 0:
            continue

        # Reset?
        if "unpatchable" in flags:
            assert "copy" not in flags, "Cannot apply both 'copy' and 'unpatchable'"
            for outOffset in outOffsets:
                f_dwpatch_epd(EPD(outOffset), Db(inputData))

        elif "copy" in flags:
            inputData_db = Db(inputData)
            inputDwordN = (len(inputData) + 3) // 4

            for outOffset in outOffsets:
                addrEPD = f_epdread_epd(EPD(outOffset))
                f_repmovsd_epd(addrEPD, EPD(inputData_db), inputDwordN)

        else:
            DoActions([SetMemory(outOffset, SetTo, Db(inputData)) for outOffset in outOffsets])
