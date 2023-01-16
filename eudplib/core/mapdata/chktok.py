#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from eudplib import utils as ut
from eudplib.localize import _

"""
General CHK class.
"""


def sectionname_format(sn: str | bytes) -> bytes:
    section_name: bytes
    if isinstance(sn, str):
        section_name = sn.encode("ascii")
    else:
        section_name = sn

    if len(section_name) < 4:
        section_name += b" " * (4 - len(section_name))

    elif len(section_name) > 4:
        raise ut.EPError(_("Length of section name cannot be longer than 4"))

    return section_name


class CHK:
    def __init__(self) -> None:
        self.sections: dict[bytes, bytes] = {}

    def loadblank(self) -> None:
        self.sections = {}

    def loadchk(self, b: bytes) -> bool:
        # this code won't handle protection methods properly such as...
        # - duplicate section name
        # - jump section protection
        #
        # this program although handles
        #  - invalid section length (too high)
        #  - unused sections

        t = self.sections  # temporarily store
        self.sections = {}

        index = 0
        while index < len(b):
            # read data
            sectionname = b[index : index + 4]
            sectionlength = ut.b2i4(b, index + 4)

            if sectionlength < 0:
                # jsp with negative section size.
                self.sections = t
                return False

            section = b[index + 8 : index + 8 + sectionlength]
            index += sectionlength + 8

            self.sections[sectionname] = section

        return True

    def clone(self) -> "CHK":
        t = CHK()
        t.sections = dict(self.sections)
        return t

    def savechk(self) -> bytes:
        # calculate output size
        blist = []
        for name, binary in self.sections.items():
            blist.append(name + ut.i2b4(len(binary)) + binary)

        fake_section = [b"ISOM"]
        import random

        fake_name = random.sample(fake_section, 1)
        blist.append(fake_name[0] + ut.i2b4(random.randint(0, 0xFFFFFFFF) | 0x80000000))
        return b"".join(blist)

    def enumsection(self) -> list[bytes]:
        return list(self.sections.keys())

    def getsection(self, sectionname: str | bytes) -> bytes:
        sectionname = sectionname_format(sectionname)
        return self.sections[sectionname]  # KeyError may be raised.

    def setsection(self, sectionname: str | bytes, b: bytes) -> None:
        sectionname = sectionname_format(sectionname)
        self.sections[sectionname] = bytes(b)

    def delsection(self, sectionname: str | bytes) -> None:
        sectionname = sectionname_format(sectionname)
        del self.sections[sectionname]

    def optimize(self) -> None:

        # Delete unused sections
        # fmt: off
        used_section = [
            b'VER ', b'VCOD', b'OWNR', b'ERA ', b'DIM ', b'SIDE', b'MTXM',
            b'UNIT', b'THG2', b'MASK', b'STRx', b'UPRP', b'MRGN', b'TRIG',
            b'MBRF', b'SPRP', b'FORC', b'COLR', b'PUNI', b'PUPx', b'PTEx',
            b'UNIx', b'UPGx', b'TECx', b'CRGB',
        ]
        # fmt: on

        unused_section = [sn for sn in self.sections.keys() if sn not in used_section]
        for sn in unused_section:
            del self.sections[sn]

        # Terrain optimization
        dim = self.getsection(b"DIM ")
        mapw = ut.b2i2(dim, 0)
        maph = ut.b2i2(dim, 2)
        terrainsize = mapw * maph

        # Omit MASK and MTXM optimization. Game desync is reported if MTXM has shorter size.
        """
        # MASK optimization : cancel 0xFFs.
        mask = self.getsection(b"MASK")
        if mask:
            clippos = 0
            for i in range(terrainsize - 1, -1, -1):
                if mask[i] != 0xFF:
                    clippos = i + 1
                    break

            mask = mask[:clippos]
            self.setsection(b"MASK", mask)

        # MTXM optimization
        # MASK optimization : cancel 0xFFs.
        mtxm = self.getsection(b"MTXM")
        clippos = 0
        for i in range(terrainsize - 1, -1, -1):
            if mtxm[2 * i] != 0x00 or mtxm[2 * i + 1] != 0x00:
                clippos = i + 1
                break

        mtxm = mtxm[: 2 * clippos]
        self.setsection(b"MTXM", mtxm)
        """

        # More optimization would be possible, but I don't care.
