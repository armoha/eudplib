# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineParam
from . import readtable

cpcache = c.curpl.GetCPCache()
_copydwn = c.Forward()
_check_copydwn = c.Memory(_copydwn, c.Exactly, 0)
_copydwn << _check_copydwn + 0
_read_end = readtable.read_end_common


@_EUDPredefineParam((ut.EPD(_read_end) + 86, ut.EPD(0x6509B0), ut.EPD(_copydwn)))
@c.EUDFunc
def f_repmovsd_epd(dstepdp, srcepdp, copydwn):
    dwread_cp_start = readtable._get(0xFFFFFFFF, 0)
    loopstart, contpoint, loopend, funcend = (c.Forward() for _ in range(4))
    c.RawTrigger(
        actions=[
            c.SetNextPtr(loopstart, dwread_cp_start),
            c.SetNextPtr(_read_end, contpoint),
            cpcache.SetDest(ut.EPD(0x6509B0)),
            c.SetNextPtr(cpcache.GetVTable(), funcend),
        ]
    )
    loopstart << c.RawTrigger(
        nextptr=dwread_cp_start,
        conditions=_check_copydwn,
        actions=c.SetNextPtr(loopstart, loopend),
    )
    contpoint << c.RawTrigger(
        nextptr=loopstart,
        actions=[
            c.SetMemory(_read_end + 344, c.Add, 1),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetMemory(_copydwn, c.Subtract, 1),
        ],
    )

    loopend << cpcache.GetVTable()
    funcend << c.NextTrigger()


@c.EUDFunc
def _memcpy(dst, src, copylen):
    from .rwcommon import br1, bw1

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if cs.EUDWhile()(copylen >= 1):
        b = br1.readbyte()
        bw1.writebyte(b)
        copylen -= 1
    cs.EUDEndWhile()


def f_memcpy(dst, src, copylen, **kwargs):
    if (
        isinstance(dst, int)
        and isinstance(src, int)
        and isinstance(copylen, int)
        and dst % 4 == src % 4 == copylen % 4 == 0
    ):
        return f_repmovsd_epd(ut.EPD(dst), ut.EPD(src), copylen // 4, **kwargs)
    return _memcpy(dst, src, copylen, **kwargs)


@c.EUDFunc
def f_memcmp(buf1, buf2, count):
    from .rwcommon import br1, br2

    br1.seekoffset(buf1)
    br2.seekoffset(buf2)

    if cs.EUDWhile()(count >= 1):
        count -= 1
        ch1 = br1.readbyte()
        ch2 = br2.readbyte()
        cs.EUDContinueIf(ch1 == ch2)
        c.EUDReturn(ch1 - ch2)
    cs.EUDEndWhile()

    c.EUDReturn(0)
