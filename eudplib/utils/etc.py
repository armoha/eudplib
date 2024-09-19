# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
import os.path
import random
import sys
from collections.abc import Iterable, Iterator, Sequence
from typing import Any, TypeVar, overload

from .. import core as c
from ..localize import _
from .eperror import EPError, ep_warn
from .exprproxy import unProxy

T = TypeVar("T")
_epd_on_epd = True


def _allow_epd_on_epd(b: bool) -> None:
    global _epd_on_epd
    _epd_on_epd = b


def EPD(p: Any, **kwargs) -> Any:  # noqa: N802
    if c.IsConstExpr(p):
        p = unProxy(p)
        if isinstance(p, c.ConstExpr) and p._is_epd():
            if _epd_on_epd:
                ep_warn(_("EPD on EPD value of ConstExpr is no-op"))
            else:
                raise EPError(_("EPD on EPD value of ConstExpr is no-op"))
        epd = (p + (-0x58A364)) // 4
        if "ret" in kwargs:
            c.SeqCompute([(kwargs["ret"][0], c.SetTo, epd)])
            return kwargs["ret"][0]
        return epd

    if c.IsEUDVariable(p):
        if sys.getrefcount(p) <= 2:
            mask = 0b111
            actions = [
                p.AddNumber(-0x58A364),
                p.SetNumberX(0, mask >> 1),
            ]
            actions.extend(
                p.SubtractNumberX((mask >> 1) << t, mask << t) for t in range(30)
            )
            c.RawTrigger(actions=actions)
            return p
        if not hasattr(EPD, "_eudf"):
            c.PushTriggerScope()
            setter = c.SetDeaths(0, c.SetTo, 0, 0)
            vaddr = setter + 20
            mask = 0b111
            actions = [
                c.SetMemory(vaddr, c.Add, -0x58A364),
                c.SetMemoryX(vaddr, c.SetTo, 0, mask >> 1),
            ]
            actions.extend(
                c.SetMemoryX(vaddr, c.Subtract, (mask >> 1) << t, mask << t)
                for t in range(30)
            )
            actions.append(setter)
            ftrg = c.RawTrigger(nextptr=0, actions=actions)
            c.PopTriggerScope()

            setattr(EPD, "_eudf", (ftrg, setter))

        ret = kwargs["ret"][0] if "ret" in kwargs else c.EUDVariable()
        ftrg, setter = getattr(EPD, "_eudf")
        nexttrg = c.Forward()
        dst = EPD(ret.getValueAddr()) if c.IsEUDVariable(ret) else ret
        c.SeqCompute(
            [
                (EPD(ftrg) + 1, c.SetTo, nexttrg),
                (EPD(setter) + 4, c.SetTo, dst),
                (EPD(setter) + 5, c.SetTo, p),
            ]
        )
        c.SetNextTrigger(ftrg)
        nexttrg << c.NextTrigger()
        return ret

    raise EPError(_("Invalid input for EPD: {}").format(p))


# -------

_string_types = (bytes, str)


def FlattenList(lst: Any, ret=None) -> list:  # noqa: N802
    if ret is None:
        ret = []

    if isinstance(lst, _string_types) or hasattr(lst, "dont_flatten"):
        ret.append(lst)
        return ret

    try:
        for item in lst:
            FlattenList(item, ret)
        return ret

    except TypeError:  # lst is not iterable
        ret.append(lst)
        return ret


def FlattenIter(lst: Any) -> Iterator:  # noqa: N802
    if isinstance(lst, _string_types) or hasattr(lst, "dont_flatten"):
        yield lst
    else:
        try:
            for item in lst:
                yield from FlattenIter(item)
        except TypeError:
            yield lst


def List2Assignable(lst: Sequence[T]) -> T | Sequence[T]:  # noqa: N802
    if len(lst) == 1:
        return lst[0]

    else:
        return lst


@overload
def Assignable2List(a: None) -> list:
    ...


@overload
def Assignable2List(a: Iterable[T]) -> list[T]:
    ...


@overload
def Assignable2List(a: T) -> list[T]:
    ...


def Assignable2List(a: Any) -> list:  # noqa: N802
    if a is None:
        return []

    if not hasattr(a, "dont_flatten"):
        try:
            return list(a)
        except TypeError:
            pass

    return [a]


cachedfunc = functools.cache


# -------

# Original code from TrigEditPlus::ConvertString_SCMD2ToRaw


def SCMD2Text(s: str) -> str:  # noqa: N802
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


def find_data_file(filename, file) -> str | bytes:
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(file)

    return os.path.join(datadir, filename)


def _rand_lst(lst: Iterable) -> list:
    lst = list(lst)
    random.shuffle(lst)
    return lst
