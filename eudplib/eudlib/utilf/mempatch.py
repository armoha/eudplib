# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ...collections.eudarray import EUDArray
from ...memio import f_dwread_epd, f_repmovsd_epd

_patch_max = 8192

patchstack = EUDArray(3 * _patch_max)
dws_top, ps_top = c.EUDVariable(), c.EUDVariable()
dwstack = EUDArray(_patch_max)


def pushpatchstack(value: c.EUDVariable | int) -> None:
    global ps_top
    patchstack[ps_top] = value
    ps_top += 1


def poppatchstack() -> c.EUDVariable:
    global ps_top
    ps_top -= 1
    return patchstack[ps_top]


@c.EUDFunc
def f_dwpatch_epd(dstepd, value):
    global dws_top

    prev_value = f_dwread_epd(dstepd)
    dws_pos = ut.EPD(dwstack) + dws_top
    c.VProc(
        [dstepd, value, dws_pos, prev_value],
        [
            dstepd.SetDest(ut.EPD(value.getDestAddr())),
            dws_pos.SetDest(ut.EPD(prev_value.getDestAddr())),
        ],
    )

    pushpatchstack(dstepd)
    pushpatchstack(dws_pos)
    pushpatchstack(1)
    dws_top += 1


@c.EUDFunc
def f_blockpatch_epd(dstepd, srcepd, dwn):
    """Patch 4*dwn bytes of memory at dstepd with memory of srcepd.

    .. note::
        After calling this function, contents at srcepd memory may change.
        Since new contents are required for :py:`f_unpatchall` to run, you
        shouldn't use the memory for any other means.
    """

    global dws_top

    # Push to stack
    pushpatchstack(dstepd)
    pushpatchstack(srcepd)
    pushpatchstack(dwn)
    copydwn = c.EUDVariable()
    endbranch, contpoint = c.Forward(), c.Forward()
    c.SeqCompute(
        [
            (dws_top, c.Add, 1),
            (copydwn, c.SetTo, 256),
            (ut.EPD(endbranch) + 1, c.SetTo, contpoint),
        ]
    )

    # Swap contents btw dstepd, srcepd
    tmpbuffer = c.Db(1024)

    if cs.EUDWhileNot()(dwn == 0):
        endbranch << c.RawTrigger(
            nextptr=0,
            conditions=dwn <= 255,
            actions=[
                c.SetNextPtr(endbranch, dwn.GetVTable()),
                dwn.SetDest(copydwn),
                c.SetNextPtr(dwn.GetVTable(), contpoint),
            ],
        )
        contpoint << c.RawTrigger(actions=dwn.SubtractNumber(256))

        f_repmovsd_epd(ut.EPD(tmpbuffer), dstepd, copydwn)
        f_repmovsd_epd(dstepd, srcepd, copydwn)
        f_repmovsd_epd(srcepd, ut.EPD(tmpbuffer), copydwn)
    cs.EUDEndWhile()


@c.EUDFunc
def f_unpatchall():
    global ps_top, dws_top
    if cs.EUDWhile()(ps_top >= 1):
        dws_top -= 1
        dwn = poppatchstack()
        unpatchsrcepd = poppatchstack()
        dstepd = poppatchstack()
        f_repmovsd_epd(dstepd, unpatchsrcepd, dwn)
    cs.EUDEndWhile()
