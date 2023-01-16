#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ...localize import _
from ...utils import b2i2, ep_warn
from .chktok import CHK


def FixMapData(chkt: CHK) -> None:
    FixUnitMap(chkt)
    FixSettings(chkt)
    ApplyRemasteredChk(chkt)
    FixMTXM0_0Null(chkt)


def FixUnitMap(chkt: CHK) -> None:
    unit = bytearray(chkt.getsection("UNIT"))

    for i in range(0, len(unit), 36):
        # Disable flags for default value
        if unit[i + 17] == 100:
            unit[i + 14] &= ~2
        if unit[i + 18] == 100:
            unit[i + 14] &= ~4
        if unit[i + 24 : i + 26] == b"\0\0":
            unit[i + 14] &= ~32
        for k in range(5):
            if unit[i + 26] & (2**k) == 0:
                unit[i + 12] &= ~(2**k)

        # Remove disabled values
        # if unit[i + 14] & 1 == 0:
        #     unit[i + 16] = 0
        if unit[i + 14] & 2 == 0:
            unit[i + 17] = 0
        if unit[i + 14] & 4 == 0:
            unit[i + 18] = 0
        if unit[i + 14] & 8 == 0:
            unit[i + 19] = 0
        if unit[i + 14] & 16 == 0:
            unit[i + 20 : i + 24] = b"\0\0\0\0"
        if unit[i + 14] & 32 == 0:
            unit[i + 24 : i + 26] = b"\0\0"
        for k in range(5):
            if unit[i + 12] & (2**k) == 0:
                unit[i + 26] &= ~(2**k)

    chkt.setsection("UNIT", unit)


def FixSettings(chkt: CHK) -> None:
    sections = (
        ("UNIx", 228, (4, 2, 1, 2, 2, 2, 2)),
        ("UPGx", 61, (2, 2, 2, 2, 2, 2)),
        ("TECx", 44, (2, 2, 2, 2)),
    )
    for name, count, settings in sections:
        data = bytearray(chkt.getsection(name))

        for i in range(count):
            if data[i] == 0:
                continue
            offset = count
            if name == "UPGx":
                offset += 1
            for setting in settings:
                for k in range(setting):
                    data[offset + setting * i + k] = 0
                offset += setting * count

        chkt.setsection(name, data)


def ApplyRemasteredChk(chkt: CHK) -> None:
    chkt.setsection("VER ", b"\xCE\0")


def FixMTXM0_0Null(chkt: CHK) -> None:
    mtxm = bytearray(chkt.getsection("MTXM"))

    null_tiles = []
    for i in range(0, len(mtxm), 2):
        if mtxm[i : i + 2] == b"\0\0":
            mtxm[i : i + 2] = b"\x01\0"
            null_tiles.append(i // 2)

    if null_tiles:
        dim = chkt.getsection("DIM")
        width = b2i2(dim, 0)

        print("Null tiles at:", ", ".join(map(lambda x: str(divmod(x, width)[::-1]), null_tiles)))
        ep_warn(
            _("[Warning] Input map has 0000.00 null tiles")
            + "\n"
            + _("Replaced them to 0000.01, because they cause desync.")
        )

    chkt.setsection("MTXM", mtxm)
