#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


def T(x: int) -> int:  # noqa: N802
    x &= 0xFFFFFFFF
    for i in range(4):
        xsq = x * x
        x = (x * (xsq * (xsq * xsq + 1) + 1) + 0x8ADA4053) & 0xFFFFFFFF
    return x


def mix(x: int, y: int) -> int:
    return T(T(x) + y + 0x10F874F3) & 0xFFFFFFFF
