# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import random

from ... import core as c
from ... import ctrlstru as cs
from ... import memio as mi
from ... import utils as ut
from ...core.mapdata.chktok import CHK
from ...eudlib.utilf.gametick import f_getgametick
from ...scdata import CurrentPlayer
from ...trigtrg import runtrigtrg as rtt
from ..inlinecode.ilcprocesstrig import _get_inline_code_list

""" Stage 3:
- Fixes nextptr modification to TRIG triggers by stage 1
- Flip property value by trig section
- Dispatch inline codes
- Create infinite executer for root
"""


def _dispatch_inline_code(
    nextptr: c.EUDVariable, trigepd: c.EUDVariable, prop: int
) -> None:
    cs0 = c.Forward()  # set cs0+20 to code_start
    cs1 = c.Forward()  # set cs1+20 to ut.EPD(code_end) + 1
    cs2 = c.Forward()  # set cs2+20 to cs_a0_epd + 4
    cs3 = c.Forward()  # set cs3+20 to cs_a0_epd + 5
    resetter = c.Forward()
    end = c.Forward()

    v = random.randint(234, 65535)
    c.VProc(
        trigepd,
        [
            trigepd.AddNumber(-prop + 2 - 12 * v),
            trigepd.SetDest(ut.EPD(0x6509B0)),
        ],
    )

    for func_id, func in _get_inline_code_list():
        code_start, code_end = func
        cs_a0_epd = ut.EPD(code_start) + (8 + 320) // 4

        t = c.Forward()
        nt = c.Forward()
        acts = [
            c.SetMemory(cs0 + 20, c.SetTo, code_start),
            c.SetMemory(cs1 + 20, c.SetTo, ut.EPD(code_end + 4)),
            c.SetMemory(cs2 + 20, c.SetTo, cs_a0_epd + 4),
            c.SetMemory(cs3 + 20, c.SetTo, cs_a0_epd + 5),
            c.SetMemory(resetter + 16, c.SetTo, ut.EPD(t + 4)),
            c.SetMemory(resetter + 20, c.SetTo, nt),
            c.SetNextPtr(t, end),
        ]
        t << c.RawTrigger(
            conditions=[c.Deaths(CurrentPlayer, c.Exactly, func_id, v)],
            actions=ut._rand_lst(acts),
        )
        nt << c.NextTrigger()

    end << c.NextTrigger()

    st1, st2, st3, st4, stf = (c.Forward() for _ in range(5))
    c.VProc(
        [trigepd, nextptr],
        [
            trigepd.AddNumber(12 * v - 1),
            # Reset t's nextptr
            resetter << c.SetNextPtr(0, 0),
            # SetNextPtr for this trigger
            # action #1
            c.SetMemory(0x6509B0, c.Add, -2 + (8 + 320) // 4 + 4),
            trigepd.SetDest(ut.EPD(st1) + 5),
            nextptr.SetDest(ut.EPD(st2) + 5),
        ],
    )
    c.RawTrigger(
        nextptr=trigepd.GetVTable(),
        actions=[
            st1 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            c.SetMemory(0x6509B0, c.Add, 1),
            cs0 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            # SetNextPtr for codeend
            # action #2
            c.SetMemory(0x6509B0, c.Add, 7),
            cs1 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            c.SetMemory(0x6509B0, c.Add, 1),
            st2 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            # This trigger sets argument for cs_a0_epd
            # cs_a0 will be SetNextPtr(trigepd + 1, nextptr) after this
            # action #3
            c.SetMemory(0x6509B0, c.Add, 7),
            cs2 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            c.SetMemory(0x6509B0, c.Add, 1),
            trigepd.SetDest(ut.EPD(st3) + 5),
            nextptr.SetDest(ut.EPD(st4) + 5),
            c.SetNextPtr(nextptr.GetVTable(), stf),
        ],
    )
    stf << c.RawTrigger(
        actions=[
            st3 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            # action #4
            c.SetMemory(0x6509B0, c.Add, 7),
            cs3 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
            c.SetMemory(0x6509B0, c.Add, 1),
            st4 << c.SetDeaths(CurrentPlayer, c.SetTo, 0, v),
        ]
    )


def _flip_prop(trigepd: c.EUDVariable) -> None:
    """Iterate through triggers and flip 'Trigger disabled' flag

    Also, dispatch inline codes
    """

    if cs.EUDWhileNot()([0x3FD56E6E <= trigepd, trigepd <= 0x3FD56E86]):
        # trigepd's nextptr may change during flipping process, so
        # we get it now.
        trigepd += 1
        nexttrig, nexttrigepd = mi.f_dwepdread_epd(trigepd)
        u = random.randint(234, 65535)
        prop = (8 + 320 + 2048) // 4 - 12 * u
        c.VProc(
            trigepd,
            [
                trigepd.AddNumber(prop - 1),
                trigepd.SetDest(ut.EPD(0x6509B0)),
            ],
        )

        # Toggle Preserved Flag
        is_inline_code, start_dispatch, set_trigepd = (c.Forward() for _ in range(3))
        c.RawTrigger(
            actions=[
                c.SetDeathsX(CurrentPlayer, c.Add, 8, u, 8),
                c.SetNextPtr(is_inline_code, set_trigepd),
            ]
        )

        # Dispatch inline code
        is_inline_code << c.RawTrigger(
            nextptr=set_trigepd,
            conditions=c.Deaths(CurrentPlayer, c.Exactly, 0x10000000, u),
            actions=[
                c.SetNextPtr(is_inline_code, start_dispatch),
                c.SetDeaths(CurrentPlayer, c.SetTo, 4, u),  # Preserve
            ],
        )
        start_dispatch << c.NextTrigger()
        _dispatch_inline_code(nexttrig, trigepd, prop)

        set_trigepd << c.NextTrigger()
        trigepd << nexttrigepd

    cs.EUDEndWhile()


def create_inject_finalizer(
    chkt: CHK, root: c.Forward | c.RawTrigger, mrgndata: bytes | None = None
) -> c.Forward:
    rtt._alloc_trigtrigger_link()
    c.EP_SetRValueStrictMode(False)

    pts = 0x51A280
    mrgn = 0x58DC60

    # Apply inline code patch
    if c.PushTriggerScope():
        ret = c.NextTrigger()

        # Revert nextptr
        triggerend = mi.f_dwread_epd(9)
        ptsprev_epd = mi.f_dwread_epd(10)
        c.VProc(
            [ptsprev_epd, triggerend],
            [
                c.SetDeaths(9, c.SetTo, 0, 0),
                c.SetDeaths(10, c.SetTo, 0, 0),
                ptsprev_epd.SetDest(ut.EPD(triggerend.getDestAddr())),
            ],
        )

        c.PushTriggerScope()
        mi.f_repmovsd_epd(0, 0, 0)
        c.PopTriggerScope()

        # revert mrgndata
        if mrgndata is None:
            mrgndata = chkt.getsection("MRGN")[: 2408 + 836]
            mrgndata_db = c.Db(mrgndata)
            mi.f_repmovsd_epd(ut.EPD(mrgn), ut.EPD(mrgndata_db), len(mrgndata) // 4)
        else:
            from ...memio.mblockio import _copydwn, _read_end

            mrgndata_db = c.Db(mrgndata)
            nexttrg = c.Forward()
            c.RawTrigger(
                nextptr=mi.f_repmovsd_epd._fstart,
                actions=[
                    c.SetMemory(_read_end + 344, c.SetTo, ut.EPD(mrgn)),
                    c.SetMemoryX(_read_end + 352, c.SetTo, 8 << 24, 0xFF000000),
                    c.SetMemory(0x6509B0, c.SetTo, ut.EPD(mrgndata_db)),
                    c.SetMemory(_copydwn, c.SetTo, len(mrgndata) // 4),
                    c.SetMemory(mi.f_repmovsd_epd._nptr, c.SetTo, nexttrg),
                ],
            )
            nexttrg << c.RawTrigger(
                actions=c.SetMemoryX(_read_end + 352, c.SetTo, 7 << 24, 0xFF000000)
            )

        # Flip TRIG properties
        i = c.EUDVariable(ut.EPD(pts + 8))
        if cs.EUDWhileNot()(i >= ut.EPD(pts + 8) + 3 * 7 + 1):
            _flip_prop(mi.f_epdread_epd(i))
            i += 3
        cs.EUDEndWhile()

        # Create payload for each players & Link them with pts
        lasttime = c.EUDVariable()
        curtime = c.EUDVariable()
        tmcheckt = c.Forward()

        for player in ut._rand_lst(range(8)):
            trs = rtt._runner_start[player]
            tre = rtt._runner_end[player]

            c.PushTriggerScope()

            # Crash preventer
            tstart, _t0 = c.Forward(), c.Forward()
            tstart << c.RawTrigger(
                prevptr=pts + player * 12 + 4,
                nextptr=trs,
                actions=c.SetNextPtr(tstart, _t0),
            )

            _t0 << c.RawTrigger(
                nextptr=tmcheckt, actions=c.SetNextPtr(tstart, trs)
            )  # reset

            c.PopTriggerScope()

            prevtstart = mi.f_dwread_epd(ut.EPD(pts) + player * 3 + 2)
            prevtend, prevtend_epd = mi.f_dwepdread_epd(ut.EPD(pts) + player * 3 + 1)

            # If there were triggers
            if cs.EUDIfNot()(prevtstart == ~(pts + player * 12 + 4)):
                (
                    orig_tstart,
                    orig_tend,
                    _runner_end_array,
                ) = rtt._alloc_trigtrigger_link()
                link_trs = c.Forward()
                vs = [prevtstart, prevtend, prevtend_epd]
                acts = [
                    # Link pts
                    c.SetMemory(pts + player * 12 + 8, c.SetTo, tstart),
                    c.SetMemory(pts + player * 12 + 4, c.SetTo, tre),
                    # Cache dlist start & end
                    prevtstart.SetDest(
                        orig_tstart + player
                        if orig_tstart._is_epd()
                        else ut.EPD(orig_tstart) + player
                    ),
                    prevtend.SetDest(
                        orig_tend + player
                        if orig_tend._is_epd()
                        else ut.EPD(orig_tend) + player
                    ),
                    prevtend_epd.AddNumber(1),
                    prevtend_epd.SetDest(ut.EPD(link_trs) + 4),
                ]
                c.VProc(ut._rand_lst(vs), ut._rand_lst(acts))
                c.VProc(
                    prevtstart,
                    [
                        # Link trs
                        link_trs << c.SetDeaths(0, c.SetTo, tre, 0),
                        prevtstart.SetDest(ut.EPD(trs) + 1),
                    ],
                )
            cs.EUDEndIf()

        if c.PushTriggerScope():
            tmcheckt << c.NextTrigger()
            f_getgametick(ret=[curtime])
            if cs.EUDIfNot()(curtime <= lasttime):  # beware QueueAddTo (-)
                c.VProc(curtime, curtime.SetDest(lasttime))
                c.SetNextTrigger(root)
            cs.EUDEndIf()

            # Set current player to 1.
            c.RawTrigger(
                nextptr=0x80000000, actions=c.SetMemory(0x6509B0, c.SetTo, 0)
            )
        c.PopTriggerScope()

        # lasttime << curtime
        f_getgametick(ret=[curtime])
        c.VProc(
            curtime,
            [
                curtime.SetDest(lasttime),
                c.SetMemory(0x6509B0, c.SetTo, 0),  # Current player = 1
            ],
        )

        # now jump to root
        c.SetNextTrigger(root)

    c.PopTriggerScope()

    return ret
