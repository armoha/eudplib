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

import functools
import itertools
import os.path
import random
import sys
from collections.abc import Callable, Collection, Iterable, Iterator
from typing import Any, overload


def EPD(p: Any) -> Any:
    return (p + (-0x58A364)) // 4


# -------


def FlattenList(l: Any) -> list:
    if isinstance(l, (bytes, str)) or hasattr(l, "dontFlatten"):
        return [l]

    try:
        ret = []
        for item in l:
            ret.extend(FlattenList(item))
        return ret

    except TypeError:  # l is not iterable
        return [l]


def eqsplit(iterable: Collection, eqr: int) -> Iterator:
    if isinstance(iterable, list):
        for i in range(0, len(iterable), eqr):
            yield iterable[i : i + eqr]

    else:
        it = iter(iterable)
        item = list(itertools.islice(it, eqr))
        while item:
            yield item
            item = list(itertools.islice(it, eqr))


def List2Assignable(l: list) -> Any | list:
    if len(l) == 1:
        return l[0]

    else:
        return l


def Assignable2List(a: Any) -> list:
    if a is None:
        return []

    elif isinstance(a, Iterable) and not hasattr(a, "dontFlatten"):
        return list(a)

    else:
        return [a]


cachedfunc = functools.cache


# -------

# Original code from TrigEditPlus::ConvertString_SCMD2ToRaw


def SCMD2Text(s: str) -> str:
    #
    # normal -> xdigitinput1 -> xdigitinput2 -> xdigitinput3 -> normal
    #        '<'           xdigit          xdigit            '>'
    #                        -> normal
    #                       '>' emit '<>'
    #                                        -> normal
    #                                        '>' emit x00
    #                                                        -> normal
    # xdigit/normal  emit '<xx'
    def toxdigit(i: str) -> int | None:
        if "0" <= i <= "9":
            return ord(i) - 48
        elif "a" <= i <= "z":
            return ord(i) - 97 + 10
        elif "A" <= i <= "Z":
            return ord(i) - 65 + 10
        else:
            return None

    state: int = 0
    buf: list[int] = []
    bufch: list[str] = []
    out: list[str] = []

    # simple fsm
    for i in s:
        if state == 0:
            if i == "<":
                state = 1
                continue

            out.append(i)

        elif state == 1:
            xdi = toxdigit(i)
            if xdi is not None:
                buf.append(xdi)
                bufch.append(i)
                state = 2
                continue

            state = 0
            out.extend(["<", i])

        elif state == 2:
            xdi = toxdigit(i)
            if xdi is not None:
                buf.append(xdi)
                bufch.append(i)
                state = 3
                continue

            state = 0
            if i == ">":
                out.append(chr(buf.pop()))
                bufch.clear()

            else:
                out.extend(["<", bufch.pop(), i])
                buf.clear()

        elif state == 3:
            state = 0
            if i == ">":
                out.append(chr(buf[0] * 16 + buf[1]))

            else:
                out.extend(["<", bufch[0], bufch[1], i])
            buf.clear()
            bufch.clear()

    return "".join(out)


StrPath = str | os.PathLike[str]
BytesPath = bytes | os.PathLike[bytes]


@overload
def find_data_file(filename: StrPath, file: StrPath) -> str:
    ...


@overload
def find_data_file(filename: BytesPath, file: BytesPath) -> bytes:
    ...


def find_data_file(filename, file):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(file)

    return os.path.join(datadir, filename)


def RandList(lst: Iterable) -> list:
    lst = list(lst)
    random.shuffle(lst)
    return lst
