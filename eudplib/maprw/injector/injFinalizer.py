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

from ... import core as c
from ... import ctrlstru as cs
from ... import trigger as trg
from ... import eudlib as sf
from ... import utils as ut
from ...trigtrg import runtrigtrg as rtt
from ..inlinecode.ilcprocesstrig import GetInlineCodeList


""" Stage 3:
- Fixes nextptr modification to TRIG triggers by stage 1
- Flip property value by trig section
- Dispatch inline codes
- Create infinite executer for root
"""


def _DispatchInlineCode(trigepd):
    cs0 = c.Forward()  # set cs0+20 to codeStart
    cs1 = c.Forward()  # set cs1+20 to ut.EPD(codeEnd) + 1
    cs2 = c.Forward()  # set cs2+20 to cs_a0_epd + 4
    cs3 = c.Forward()  # set cs3+20 to cs_a0_epd + 5
    resetter = c.Forward()
    end = c.Forward()

    nextptr = sf.f_dwread_epd(trigepd + 1)

    cs.DoActions(c.SetMemory(0x6509B0, c.SetTo, trigepd + 2))

    for funcID, func in GetInlineCodeList():
        codeStart, codeEnd = func
        cs_a0_epd = ut.EPD(codeStart) + (8 + 320) // 4

        t = c.Forward()
        nt = c.Forward()
        t << c.RawTrigger(
            conditions=[c.Deaths(c.CurrentPlayer, c.Exactly, funcID, 0)],
            actions=[
                c.SetMemory(cs0 + 20, c.SetTo, codeStart),
                c.SetMemory(cs1 + 20, c.SetTo, ut.EPD(codeEnd + 4)),
                c.SetMemory(cs2 + 20, c.SetTo, cs_a0_epd + 4),
                c.SetMemory(cs3 + 20, c.SetTo, cs_a0_epd + 5),
                c.SetMemory(resetter + 16, c.SetTo, ut.EPD(t + 4)),
                c.SetMemory(resetter + 20, c.SetTo, nt),
                c.SetNextPtr(t, end),
            ],
        )
        nt << c.NextTrigger()

    end << c.NextTrigger()

    cs.DoActions(
        [
            # Reset t's nextptr
            resetter << c.SetNextPtr(0, 0),
            # SetNextPtr for this trigger
            # action #1
            c.SetMemory(0x6509B0, c.Add, -2 + (8 + 320) // 4 + 4),
            c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, trigepd + 1),
            c.SetMemory(0x6509B0, c.Add, 1),
            cs0 << c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, 0),
            # SetNextPtr for codeend
            # action #2
            c.SetMemory(0x6509B0, c.Add, 7),
            cs1 << c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, nextptr),
            # This trigger sets argument for cs_a0_epd
            # cs_a0 will be SetNextPtr(trigepd + 1, nextptr) after this
            # action #3
            c.SetMemory(0x6509B0, c.Add, 7),
            cs2 << c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, trigepd + 1),
            # action #4
            c.SetMemory(0x6509B0, c.Add, 7),
            cs3 << c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetMemoryEPD(c.CurrentPlayer, c.SetTo, nextptr),
        ]
    )


@c.EUDFunc
def _FlipProp(trigepd):
    """Iterate through triggers and flip 'Trigger disabled' flag

    Also, dispatch inline codes
    """

    if cs.EUDWhileNot()([trigepd >= 0x3FD56E6E, trigepd <= 0x3FD56E86]):
        prop_epd = trigepd + (8 + 320 + 2048) // 4
        # trigepd's nextptr may change during flipping process, so
        # we get it now.
        nexttrigepd = sf.f_epdread_epd(trigepd + (4 // 4))

        if cs.EUDIf()(c.Deaths(prop_epd, c.Exactly, 4, 0)):  # Preserved
            sf.f_dwwrite_epd(prop_epd, 8)  # Disable now
        if cs.EUDElse()():
            sf.f_dwsubtract_epd(prop_epd, 8)
        cs.EUDEndIf()

        # Dispatch inline code
        if cs.EUDIf()(c.Deaths(prop_epd, c.Exactly, 0x10000000, 0)):
            sf.f_dwwrite_epd(prop_epd, 4)  # Preserve
            _DispatchInlineCode(trigepd)
        cs.EUDEndIf()

        trigepd << nexttrigepd

    cs.EUDEndWhile()


def CreateInjectFinalizer(chkt, root):
    rtt.AllocTrigTriggerLink()

    pts = 0x51A280
    mrgn = 0x58DC60

    # Apply inline code patch
    if c.PushTriggerScope():
        ret = c.NextTrigger()

        # Revert nextptr
        triggerend = sf.f_dwread_epd(9)
        ptsprev_epd = sf.f_dwread_epd(10)
        sf.f_dwwrite_epd(ptsprev_epd, triggerend)
        cs.DoActions([c.SetDeaths(9, c.SetTo, 0, 0), c.SetDeaths(10, c.SetTo, 0, 0)])

        # revert mrgndata
        mrgndata = chkt.getsection("MRGN")[:2408 + 836]
        mrgndata_db = c.Db(mrgndata)
        sf.f_repmovsd_epd(ut.EPD(mrgn), ut.EPD(mrgndata_db), len(mrgndata) // 4)

        # Flip TRIG properties
        i = c.EUDVariable()
        if cs.EUDWhile()(i <= 7):
            _FlipProp(sf.f_epdread_epd(ut.EPD(pts + 8) + i + i + i))
            i << i + 1
        cs.EUDEndWhile()

        # Create payload for each players & Link them with pts
        lasttime = c.EUDVariable()
        curtime = c.EUDVariable()
        tmcheckt = c.Forward()

        for player in range(8):
            trs = rtt._runner_start[player]
            tre = rtt._runner_end[player]

            c.PushTriggerScope()

            # Crash preventer
            tstart, _t0 = c.Forward(), c.Forward()
            tstart << c.RawTrigger(
                prevptr=pts + player * 12 + 4,
                nextptr=trs,
                actions=[c.SetNextPtr(tstart, _t0)],
            )

            _t0 << c.RawTrigger(
                nextptr=tmcheckt,
                actions=[
                    # reset
                    c.SetNextPtr(tstart, trs)
                ],
            )

            c.PopTriggerScope()

            prevtstart = sf.f_dwread_epd(ut.EPD(pts + player * 12 + 8))
            prevtend = sf.f_dwread_epd(ut.EPD(pts + player * 12 + 4))

            # If there were triggers
            if cs.EUDIfNot()(prevtstart == ~(pts + player * 12 + 4)):
                cs.DoActions(
                    [
                        # Link pts
                        c.SetMemory(pts + player * 12 + 8, c.SetTo, tstart),
                        c.SetMemory(pts + player * 12 + 4, c.SetTo, tre),
                        # Link trs
                        c.SetMemory(trs + 4, c.SetTo, prevtstart),
                        c.SetMemory(prevtend + 4, c.SetTo, tre),
                        # Cache dlist start & end
                        c.SetMemory(rtt.orig_tstart + player * 4, c.SetTo, prevtstart),
                        c.SetMemory(rtt.orig_tend + player * 4, c.SetTo, prevtend),
                    ]
                )
            cs.EUDEndIf()

        if c.PushTriggerScope():
            tmcheckt << c.NextTrigger()
            curtime << sf.f_getgametick()
            if cs.EUDIf()(lasttime < curtime):
                lasttime << curtime
                cs.EUDJump(root)
            cs.EUDEndIf()

            # Set current player to 1.
            cs.DoActions(c.SetMemory(0x6509B0, c.SetTo, 0))

            cs.EUDJump(0x80000000)
        c.PopTriggerScope()

        # lasttime << curtime
        curtime << sf.f_getgametick()
        lasttime << curtime

        cs.DoActions(c.SetMemory(0x6509B0, c.SetTo, 0))  # Current player = 1

        # now jump to root
        cs.EUDJump(root)

    c.PopTriggerScope()

    return ret
