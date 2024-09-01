#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from ...core import Db, SetMemory, SetTo
from ...ctrlstru import DoActions
from ...memio import f_epdread_epd, f_repmovsd_epd
from ...utils import EPD
from .mempatch import f_dwpatch_epd

_data = []


def _add_datadumper(input_data, out_offsets, flags):
    _data.append((input_data, out_offsets, flags))


def _f_datadumper():
    for input_data, out_offsets, flags in _data:
        if len(out_offsets) == 0:
            continue

        # Reset?
        if "unpatchable" in flags:
            assert "copy" not in flags, "Cannot apply both 'copy' and 'unpatchable'"
            for out_offset in out_offsets:
                f_dwpatch_epd(EPD(out_offset), Db(input_data))

        elif "copy" in flags:
            input_data_db = Db(input_data)
            input_dwordn = (len(input_data) + 3) // 4

            for out_offset in out_offsets:
                addr_epd = f_epdread_epd(EPD(out_offset))
                f_repmovsd_epd(addr_epd, EPD(input_data_db), input_dwordn)

        else:
            DoActions(
                [
                    SetMemory(out_offset, SetTo, Db(input_data))
                    for out_offset in out_offsets
                ]
            )
