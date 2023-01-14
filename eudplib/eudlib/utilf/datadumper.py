#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2023 Armoha

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
from ...core import Db, SetMemory, SetTo
from .mempatch import f_dwpatch_epd
from ..memiof import f_repmovsd_epd, f_epdread_epd
from ...utils import EPD
from ...ctrlstru import DoActions

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
