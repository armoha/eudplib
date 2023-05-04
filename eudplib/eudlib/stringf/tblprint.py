#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...localize import _
from ..memiof import (
    f_dwepdread_epd,
    f_dwwrite,
    f_epdread_epd,
    f_repmovsd_epd,
    f_setcurpl,
    f_wread_epd,
)
from ..utilf import IsUserCP, f_getuserplayerid
from .cpprint import f_cpstr_print
from .eudprint import f_dbstr_print
from .fmtprint import f_sprintf


@c.EUDTypedFunc([c.StatText])
def GetTBLAddr(tblId):
    STAT_TEXT_POINTER = ut.EPD(0x6D5A30)  # TODO: hardcode 0x19184660 ?
    add_TBL_ptr, add_TBL_epd = c.Forward(), c.Forward()
    check_pointer = c.MemoryEPD(STAT_TEXT_POINTER, c.Exactly, 0)
    if cs.EUDIfNot()(check_pointer):
        from ...core.variable.evcommon import _ev

        f_dwepdread_epd(STAT_TEXT_POINTER, ret=[_ev[4], ut.EPD(add_TBL_epd) + 5])
        c.VProc(_ev[4], _ev[4].SetDest(ut.EPD(check_pointer) + 2))
        c.VProc(_ev[4], _ev[4].SetDest(ut.EPD(add_TBL_ptr) + 5))
    cs.EUDEndIf()
    r, m = c.f_div(tblId, 2)
    c.RawTrigger(conditions=m.Exactly(1), actions=m.SetNumber(2))
    c.RawTrigger(actions=add_TBL_epd << r.AddNumber(0))
    ret = f_wread_epd(r, m)
    c.RawTrigger(actions=add_TBL_ptr << ret.AddNumber(0))
    c.EUDReturn(ret)


def f_settbl(tblID, offset, *args, encoding=None):
    args = ut.FlattenList(args)
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = c.StatText._encoding

    if encoding.casefold() == "UTF-8".casefold():
        if isinstance(args[-1], str):
            if args[-1][-1] != "\u2009":
                args[-1] = args[-1] + "\u2009"
        else:
            args.append("\u2009")

    return f_dbstr_print(dst, *args, encoding=encoding)


def f_settbl2(tblID, offset, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = c.StatText._encoding

    return f_dbstr_print(dst, *args, EOS=False, encoding=encoding)


def f_settblf(tblID, offset, format_string, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = c.StatText._encoding

    if encoding.casefold() == "UTF-8".casefold() and format_string[-1] != "\u2009":
        format_string += "\u2009"

    return f_sprintf(dst, format_string, *args, encoding=encoding)


def f_settblf2(tblID, offset, format_string, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = c.StatText._encoding

    return f_sprintf(dst, format_string, *args, EOS=False, encoding=encoding)


_eprintln2_template = None
_eprintln2_print = c.Forward()
_eprintln2_EOS = c.Forward()
_eprintln2_end = c.Forward()


def f_eprintln2(*args) -> None:
    global _eprintln2_template
    if _eprintln2_template is None:
        _eprintln2_template = c.Forward()

        c.PushTriggerScope()
        _eprintln2_template << c.NextTrigger()

        if cs.EUDExecuteOnce()():
            # [871] Unit's waypoint list is full.
            ptr = GetTBLAddr(871)
            f_dwwrite(ptr, ut.b2i4(b"\r\r\r\r"))
            epd = ut.EPD(ptr) + 1
        cs.EUDEndExecuteOnce()

        if cs.EUDIf()(IsUserCP()):
            f_setcurpl(epd)
            _eprintln2_print << c.RawTrigger(nextptr=0)
            _eprintln2_EOS << c.RawTrigger(actions=c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0))
            f_setcurpl(f_getuserplayerid())
        cs.EUDEndIf()
        _eprintln2_end << c.RawTrigger(nextptr=0)
        c.PopTriggerScope()

    _print, _next = c.Forward(), c.Forward()
    c.RawTrigger(
        nextptr=_eprintln2_template,
        actions=[
            c.SetNextPtr(_eprintln2_print, _print),
            c.SetNextPtr(_eprintln2_end, _next),
        ],
    )
    _print << c.NextTrigger()
    f_cpstr_print(*args, EOS=False, encoding="UTF-8")
    c.SetNextTrigger(_eprintln2_EOS)
    _next << c.NextTrigger()


def _f_initstattext() -> None:
    if not c.StatText._data:
        return

    statText_db = c.Db(c.StatText._data)
    inputDwordN = (len(c.StatText._data) + 3) // 4

    addrEPD = f_epdread_epd(ut.EPD(0x6D5A30))
    f_repmovsd_epd(addrEPD, ut.EPD(statText_db), inputDwordN)


def _AddStatText(tbl: bytes) -> None:
    tblCount = ut.b2i2(tbl)
    newTbl = ut.i2b2(tblCount)
    tblOffset = 2 * (tblCount + 1)
    if tblCount % 2 == 0:
        tblOffset += 2
    tblContents = []
    utf8DecodableCount = tblCount
    cp949DecodableCount = tblCount

    for i in range(tblCount):
        k = 2 * (i + 1)
        tblStart = ut.b2i2(tbl, k)
        tblEnd = ut.b2i2(tbl, k + 2)
        if i == tblCount - 1:
            tblEnd = len(tbl)
        tblContent = tbl[tblStart:tblEnd] + b"\0\0\0"
        while len(tblContent) % 4 >= 1:
            tblContent += b"\0"
        newTbl += ut.i2b2(tblOffset)
        tblContents.append(tblContent)
        tblOffset += len(tblContent)

        try:
            tblContent.decode("utf-8")
        except UnicodeDecodeError:
            utf8DecodableCount -= 1
        try:
            tblContent.decode("cp949")
        except UnicodeDecodeError:
            cp949DecodableCount -= 1

    if tblCount % 2 == 0:
        newTbl += b"\0\0"

    for tblContent in tblContents:
        newTbl += tblContent

    if utf8DecodableCount < cp949DecodableCount:
        c.StatText._encoding = "CP949"

    c.StatText._data = newTbl
