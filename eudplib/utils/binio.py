#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

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

from collections.abc import ByteString, Iterator, Sequence


def b2i1(b: Sequence[int], index: int = 0) -> int:
    return b[index]


def b2i2(b: Sequence[int], index: int = 0) -> int:
    return b[index] | (b[index + 1] << 8)


def b2i4(b: Sequence[int], index: int = 0) -> int:
    return b[index] | (b[index + 1] << 8) | (b[index + 2] << 16) | (b[index + 3] << 24)


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
