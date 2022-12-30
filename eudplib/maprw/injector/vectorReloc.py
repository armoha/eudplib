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

from eudplib import utils as ut

from ... import core as c
from ...core.allocator.pbuffer import Payload
from ...core.mapdata.chktok import CHK
from ...core.mapdata.stringmap import GetStringMap, GetStringSectionName
from ...localize import _
from ...trigtrg import trigtrg as tt

""" Stage 1 : works in TRIG section.
- Check if EUD is available. If not, defeat
- Initialize stage 2 & execute it
- Modifies TRIG rawtrigger's nextptr. Modification is fixed in stage 3.
"""
trglist = []


def Trigger(players=[tt.AllPlayers], *args, **kwargs) -> None:
    global trglist
    trglist.append(tt.Trigger(players=players, *args, **kwargs))


def CopyDeaths(iplayer, oplayer, copyepd: bool = False, initvalue: int | None = None) -> None:
    if initvalue is None:
        if copyepd:
            initvalue = tt.EPD(0)
        else:
            initvalue = 0

    Trigger(actions=tt.SetDeaths(oplayer, tt.SetTo, initvalue, 0))

    for i in ut.RandList(range(2, 32)):
        if copyepd:
            subval = 2 ** (i - 2)

        else:
            subval = 2**i

        Trigger(
            conditions=[tt.DeathsX(iplayer, tt.AtLeast, 1, 0, 2**i)],
            actions=tt.SetDeaths(oplayer, tt.Add, subval, 0),
        )


def CreateVectorRelocator(chkt: CHK, payload: Payload) -> None:
    global trglist

    str_section = GetStringMap().SaveTBL()

    """
    Algorithm credit to klassical_31@naver.com

    Overall algorithm : STR <-> MRGN cycle

    MRGN:
      SetMemory(payload, Add, payload_offset // 4)

    MRGN <-> STR0  =  Trigger(actions=[
             STR1        [SetMemory(
                            mrgn.action[i].player,
                            Add,
                            prttable[j+packn] - prttable[j]
                          ) for i in range(packn)],
             STR2        SetNextPtr(mrgn, STR[k+1])
             ...      )
    """

    mrgn = 0x58DC60
    packn = 15

    #############
    # STR SECTION
    #############
    str_sled = []
    mrgn_ort = mrgn + 836
    sledheader_prt = b"\0\0\0\0" + ut.i2b4(mrgn)
    sledheader_ort = b"\0\0\0\0" + ut.i2b4(mrgn_ort)

    # apply prt
    prttrg_start = 2408 * len(str_sled)  # = 0
    # mrgn.action[i].player = EPD(payload_offset) + prevoffset[i]
    prevoffset = [-1] * packn
    for i in range(0, len(payload.prttable), packn):
        prts = list(map(lambda x: x // 4, payload.prttable[i : i + packn]))
        prts = prts + [-1] * (packn - len(prts))  # -1 : dummy space
        pch = [prts[j] - prevoffset[j] for j in range(packn)]
        str_sled.append(
            sledheader_prt
            + tt.Trigger(
                players=[tt.AllPlayers],
                actions=[
                    tt.SetMemory(mrgn + 328 + 32 * j + 16, tt.Add, pch[j]) for j in range(packn)
                ],
            )
        )

        prevoffset = prts

    # apply ort
    orttrg_start = 2408 * len(str_sled)  # = 0
    # mrgn.action[i].player = EPD(payload_offset) + prevoffset[i]
    prevoffset = [-1] * packn
    for i in range(0, len(payload.orttable), packn):
        orts = list(map(lambda x: x // 4, payload.orttable[i : i + packn]))
        orts = orts + [-1] * (packn - len(orts))  # -1 : dummy space
        pch = [orts[j] - prevoffset[j] for j in range(packn)]
        str_sled.append(
            sledheader_ort
            + tt.Trigger(
                players=[tt.AllPlayers],
                actions=[
                    tt.SetMemory(mrgn_ort + 328 + 32 * j + 16, tt.Add, pch[j])
                    for j in range(packn)
                ],
            )
        )

        prevoffset = orts

    # jump to ort
    str_sled.append(
        sledheader_ort
        + tt.Trigger(
            players=[tt.AllPlayers],
            actions=[
                [
                    tt.SetMemory(mrgn_ort + 328 + 32 * j + 16, tt.Add, 0xFFFFFFFF - prevoffset[j])
                    for j in range(packn)
                ],
                tt.SetMemory(mrgn_ort + 4, tt.Add, 4),  # skip garbage area
            ],
        )
    )

    # sled completed
    str_sled = b"".join(str_sled)

    str_padding_length = -len(str_section) & 3
    strsled_offset = len(str_section) + str_padding_length + 0x191943C8
    payload_offset = strsled_offset + len(str_sled) + 4
    str_section = str_section + bytes(str_padding_length) + str_sled + b"\0\0\0\0" + payload.data
    chkt.setsection(GetStringSectionName(), str_section)

    ##############
    # MRGN SECTION
    ##############
    mrgn_trigger = bytearray()
    mrgn_trigger_prt = (
        bytes(4)
        + ut.i2b4(prttrg_start + strsled_offset)
        + tt.Trigger(
            players=[tt.AllPlayers],
            actions=[
                # SetDeaths actions in MRGN initially points to EPD(payload - 4)
                [
                    tt.SetMemory(payload_offset - 4, tt.Add, payload_offset // 4)
                    for _ in range(packn)
                ],
                tt.SetMemory(mrgn + 4, tt.Add, 2408),
            ],
        )
        + bytes(836)
    )
    mrgn_trigger_ort = (
        bytes(836 + 4)
        + ut.i2b4(orttrg_start + strsled_offset)
        + tt.Trigger(
            players=[tt.AllPlayers],
            actions=[
                [tt.SetMemory(payload_offset - 4, tt.Add, payload_offset) for _ in range(packn)],
                tt.SetMemory(mrgn_ort + 4, tt.Add, 2408),
            ],
        )
    )
    for b1, b2 in zip(mrgn_trigger_prt, mrgn_trigger_ort):
        mrgn_trigger.append(b1 ^ b2)

    oldmrgnraw = chkt.getsection("MRGN")
    mrgn_section = bytes(mrgn_trigger) + oldmrgnraw[2408 + 836 :]
    if len(mrgn_section) != 5100:
        raise RuntimeError(_("MRGN section size bug"))
    chkt.setsection("MRGN", mrgn_section)

    ##############
    # TRIG SECTION
    ##############
    trglist.clear()

    # pts[player].lasttrigger->next = value(strs) + strsled_offset

    pts = 0x51A280
    curpl = 0x6509B0

    for player in ut.RandList(range(8)):
        triggerend = ~(0x51A284 + player * 12)

        Trigger(
            players=[player],
            actions=[
                tt.SetMemory(curpl, tt.SetTo, ut.EPD(pts + 12 * player + 4)),
                tt.SetDeaths(9, tt.SetTo, triggerend, 0),  # Used in stage 2
            ],
        )

    # read pts[player].lasttrigger
    for e in ut.RandList(range(2, 32)):
        Trigger(
            conditions=tt.DeathsX(tt.CurrentPlayer, tt.AtLeast, 1, 0, 2**e),
            actions=tt.SetDeaths(11, tt.Add, 2**e, 0),
        )

    # apply to curpl
    Trigger(
        actions=[
            tt.SetDeaths(10, tt.SetTo, ut.EPD(4), 0),
            tt.SetMemory(curpl, tt.SetTo, ut.EPD(4)),
        ]
    )
    for e in ut.RandList(range(2, 32)):
        Trigger(
            conditions=tt.DeathsX(11, tt.AtLeast, 1, 0, 2**e),
            actions=[
                # tt.SetDeaths(11, tt.Subtract, 2 ** e, 0),
                # used for nextptr recovery in stage 3
                tt.SetDeaths(10, tt.Add, 2 ** (e - 2), 0),
                tt.SetMemory(curpl, tt.Add, 2 ** (e - 2)),
            ],
        )

    # now curpl = EPD(value(ptsprev) + 4)
    # value(EPD(value(ptsprev) + 4)) = strs + payload_offset
    # CopyDeaths(tt.EPD(strs), tt.CurrentPlayer, False, strsled_offset)
    Trigger(
        actions=[
            tt.SetDeaths(tt.CurrentPlayer, tt.SetTo, strsled_offset, 0),
            tt.SetDeaths(11, tt.SetTo, 0, 0),
        ]
    )

    # Done!
    trigdata = b"".join(trglist)

    # Stage 1 created

    # -------

    # Previous rawtrigger datas

    oldtrigraw = chkt.getsection("TRIG")
    oldtrigs = [oldtrigraw[i : i + 2400] for i in range(0, len(oldtrigraw), 2400)]
    proc_trigs = []

    # Collect only enabled triggers
    for trig in oldtrigs:
        trig = bytearray(trig)
        flag = ut.b2i4(trig, 320 + 2048)
        if flag & 8:  # Trigger already disabled
            pass

        flag ^= 8  # Disable it temporarily. It will be re-enabled at stage 3
        trig[320 + 2048 : 320 + 2048 + 4] = ut.i2b4(flag)
        proc_trigs.append(bytes(trig))

    oldtrigraw_processed = b"".join(proc_trigs)
    chkt.setsection("TRIG", trigdata + oldtrigraw_processed)
