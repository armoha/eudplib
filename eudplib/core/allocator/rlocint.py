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


class RlocInt_C:  # noqa: N801

    """Relocatable int"""

    def __init__(self, offset: int, rlocmode: int) -> None:
        self.offset: int = offset
        self.rlocmode: int = rlocmode

    def __add__(self, rhs: _RlocInt) -> "RlocInt_C":
        if isinstance(rhs, RlocInt_C):
            return RlocInt_C(self.offset + rhs.offset, self.rlocmode + rhs.rlocmode)
        else:
            return RlocInt_C(self.offset + rhs, self.rlocmode)

    def __sub__(self, rhs: _RlocInt) -> "RlocInt_C":
        if isinstance(rhs, RlocInt_C):
            return RlocInt_C(
                self.offset - rhs.offset,
                self.rlocmode - rhs.rlocmode,
            )
        else:
            return RlocInt_C(self.offset - rhs, self.rlocmode)

    def __mul__(self, other: _RlocInt) -> "RlocInt_C":
        if isinstance(other, RlocInt_C):
            ut.ep_assert(
                other.rlocmode == 0, _("Cannot divide RlocInt with non-const")
            )
            other = other.offset

        return RlocInt_C(self.offset * other, self.rlocmode * other)

    def __floordiv__(self, other: _RlocInt) -> "RlocInt_C":
        if isinstance(other, RlocInt_C):
            ut.ep_assert(
                other.rlocmode == 0, _("Cannot divide RlocInt with non-const")
            )
            other = other.offset
        ut.ep_assert(other != 0, _("Divide by zero"))
        ut.ep_assert(
            (self.rlocmode == 0)
            or (self.rlocmode % other == 0 and self.offset % other == 0),
            _("RlocInt not divisible by {}").format(other),
        )
        return RlocInt_C(self.offset // other, self.rlocmode // other)

    def __str__(self) -> str:
        return "RlocInt(0x%08X, %d)" % (self.offset, self.rlocmode)

    def __repr__(self) -> str:
        return str(self)


def RlocInt(offset: int, rlocmode: int) -> RlocInt_C:  # noqa: N802
    return RlocInt_C(offset, rlocmode)


def toRlocInt(x: _RlocInt) -> RlocInt_C:  # noqa: N802
    """Convert int/RlocInt to rlocint"""

    if isinstance(x, RlocInt_C):
        return x

    else:
        return RlocInt_C(x, 0)
