#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from typing import TypeAlias

from eudplib import utils as ut
from eudplib.localize import _

_RlocInt: TypeAlias = "int | RlocInt_C"


class RlocInt_C:

    """Relocatable int"""

    def __init__(self, offset: int, rlocmode: int) -> None:
        self.offset: int = offset
        self.rlocmode: int = rlocmode

    # http://stackoverflow.com/questions/18794169/pythons-radd-doesnt-work-for-c-defined-types
    # Some obscure type can fludge into 'self' slot, so I called it 'lhs'
    # rather than self.
    def __add__(lhs, rhs: _RlocInt) -> "RlocInt_C":
        if isinstance(lhs, RlocInt_C):  # Call from radd
            if isinstance(rhs, RlocInt_C):
                return RlocInt_C(lhs.offset + rhs.offset, lhs.rlocmode + rhs.rlocmode)
            else:
                return RlocInt_C((lhs.offset + rhs) & 0xFFFFFFFF, lhs.rlocmode)
        else:
            return RlocInt_C((rhs.offset + lhs) & 0xFFFFFFFF, rhs.rlocmode)

    def __sub__(lhs, rhs: _RlocInt) -> "RlocInt_C":
        lhs = toRlocInt(lhs)
        if isinstance(rhs, RlocInt_C):
            return RlocInt_C(
                (lhs.offset - rhs.offset) & 0xFFFFFFFF,
                (lhs.rlocmode - rhs.rlocmode) & 0xFFFFFFFF,
            )
        else:
            return RlocInt_C((lhs.offset - rhs) & 0xFFFFFFFF, lhs.rlocmode)

    def __mul__(self, other: _RlocInt) -> "RlocInt_C":
        if isinstance(other, RlocInt_C):
            ut.ep_assert(other.rlocmode == 0, _("Cannot divide RlocInt with non-const"))
            other = other.offset

        return RlocInt_C((self.offset * other) & 0xFFFFFFFF, self.rlocmode * other)

    def __floordiv__(self, other: _RlocInt) -> "RlocInt_C":
        if isinstance(other, RlocInt_C):
            ut.ep_assert(other.rlocmode == 0, _("Cannot divide RlocInt with non-const"))
            other = other.offset
        ut.ep_assert(other != 0, _("Divide by zero"))
        ut.ep_assert(
            (self.rlocmode == 0)
            or (self.rlocmode % other == 0 and self.offset % other == 0),
            _("RlocInt not divisible by {}").format(other),
        )
        return RlocInt_C((self.offset // other) & 0xFFFFFFFF, self.rlocmode // other)

    def __str__(self) -> str:
        return "RlocInt(0x%08X, %d)" % (self.offset, self.rlocmode)

    def __repr__(self) -> str:
        return str(self)


def RlocInt(offset: int, rlocmode: int) -> RlocInt_C:
    return RlocInt_C(offset & 0xFFFFFFFF, rlocmode & 0xFFFFFFFF)


def toRlocInt(x: _RlocInt) -> RlocInt_C:
    """Convert int/RlocInt to rlocint"""

    if isinstance(x, RlocInt_C):
        return x

    else:
        return RlocInt_C(x & 0xFFFFFFFF, 0)
