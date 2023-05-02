#!/usr/bin/python

from collections.abc import ByteString

from eudplib import utils as ut

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
trglist: list[bytes] = []


def Trigger(
    *,
    # FIXME: Cannot determine type of "AllPlayers" [has-type]
    players: list[tt.Player] = [17],
    conditions: list[bytes] | bytes = [],
    actions: list[bytes] | bytes = [],
) -> None:
    global trglist
    trglist.append(tt.Trigger(players, conditions, actions))


def InitializePayload(
    chkt: CHK, payload: Payload, mrgndata: ByteString | None = None
) -> None:
    strmap = GetStringMap()
    if strmap is None:
        raise ut.EPError(_("Must use LoadMap first"))
    str_section = strmap.SaveTBL()
    str_padding = -len(str_section) & 3
    payload_offset = 0x191943C8 + len(str_section) + str_padding

    orig_payload = payload.data
    new_payload = bytearray(orig_payload)

    for prt in payload.prttable:
        v = ut.b2i4(new_payload[prt : prt + 4])
        v += payload_offset // 4
        new_payload[prt : prt + 4] = ut.i2b4(v)
    for ort in payload.orttable:
        v = ut.b2i4(new_payload[ort : ort + 4])
        v += payload_offset
        new_payload[ort : ort + 4] = ut.i2b4(v)

    str_section = str_section + bytes(str_padding) + new_payload
    chkt.setsection(GetStringSectionName(), str_section)

    if mrgndata is not None:
        orig_mrgn = chkt.getsection("MRGN")
        mrgn_section = []
        for i in range(0, len(orig_mrgn), 4):
            if i % 20 == 16:  # remove name
                orig = ut.b2i2(orig_mrgn, i + 2) << 16
            else:
                orig = ut.b2i4(orig_mrgn, i)
            obfus = ut.b2i4(mrgndata, i)
            if obfus > orig:
                orig += 1 << 32
            mrgn_section.append(ut.i2b4(orig - obfus))
        chkt.setsection("MRGN", b"".join(mrgn_section))

    ##############
    # TRIG SECTION
    ##############
    trglist.clear()

    # pts[player].lasttrigger->next = value(strs) + strsled_offset

    pts = 0x51A284
    curpl = 0x6509B0

    for player in ut.RandList(range(8)):
        triggerend = ~(pts + player * 12)

        Trigger(
            players=[player],
            actions=[
                tt.SetMemory(curpl, tt.SetTo, ut.EPD(pts + 12 * player)),
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
            tt.SetDeaths(tt.CurrentPlayer, tt.SetTo, payload_offset, 0),
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
