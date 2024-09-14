# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterator, Sequence


def b2i1(b: Sequence[int], index: int = 0) -> int:
    return b[index]


def b2i2(b: Sequence[int], index: int = 0) -> int:
    return b[index] | (b[index + 1] << 8)


def b2i4(b: Sequence[int], index: int = 0) -> int:
    return (
        b[index] | (b[index + 1] << 8) | (b[index + 2] << 16) | (b[index + 3] << 24)
    )


def i2b1(i: int) -> bytes:
    return bytes((i & 0xFF,))


def i2b2(i: int) -> bytes:
    i &= 0xFFFF
    return bytes((i & 0xFF, (i >> 8) & 0xFF))


def i2b4(i: int) -> bytes:
    i &= 0xFFFFFFFF
    return bytes((i & 0xFF, (i >> 8) & 0xFF, (i >> 16) & 0xFF, (i >> 24) & 0xFF))


def bits(n: int) -> Iterator[int]:
    n = n & 0xFFFFFFFF
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b
