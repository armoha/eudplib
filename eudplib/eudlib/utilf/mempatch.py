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

from eudplib import core as c, ctrlstru as cs, utils as ut, trigger as t
from ..eudarray import EUDArray
from ..memiof import f_dwread_epd, f_dwwrite_epd, f_repmovsd_epd

patchMax = 8192

patchstack = EUDArray(3 * patchMax)
dws_top, ps_top = c.EUDVariable(), c.EUDVariable()
dwstack = EUDArray(patchMax)


def pushpatchstack(value):
    global ps_top
    patchstack[ps_top] = value
    ps_top += 1


def poppatchstack():
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
    """ Patch 4*dwn bytes of memory at dstepd with memory of srcepd.

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
    dws_top += 1

    # Swap contents btw dstepd, srcepd
    tmpbuffer = c.Db(1024)

    if cs.EUDWhile()(dwn > 0):
        copydwn = c.EUDVariable()
        copydwn << 256
        t.Trigger(dwn <= 256, copydwn.SetNumber(dwn))
        dwn -= copydwn

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
