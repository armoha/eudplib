#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib.utils import EPD, ep_assert

from ..memio import (
    EUDByteWriter,
    f_dwread_epd,
    f_memcpy,
    f_setcurpl2cpcache,
)
from ..scdata import CurrentPlayer, TrgUnit

_PROV_MAXBUFFER = 0x57F0D8
_cmdqlen = c.EUDVariable()
_CMDQLEN = 0x654AA0
_len_cache = c.Memory(_CMDQLEN, c.Exactly, 0)


@c.EUDFunc
def _update_cmdqlen():
    if cs.EUDIfNot()(_len_cache):
        f_dwread_epd(EPD(0x654AA0), ret=[_cmdqlen])
        c.VProc(_cmdqlen, _cmdqlen.QueueAssignTo(EPD(_len_cache) + 2))
    cs.EUDEndIf()


def _get_cmdqlen():
    _update_cmdqlen()
    return _cmdqlen


def _set_cmdqlen(new_len):
    ep_assert(c.IsEUDVariable(new_len))
    c.VProc(
        [new_len, _cmdqlen],
        [
            new_len.QueueAssignTo(_cmdqlen),
            _cmdqlen.QueueAssignTo(EPD(_CMDQLEN)),
        ],
    )
    c.VProc(_cmdqlen, _cmdqlen.SetDest(EPD(_len_cache) + 2))


class QueueGameCommandHelper:
    def __init__(self, size):
        self.size = size

    def __enter__(self):
        self.cmdqlen = _get_cmdqlen()
        self.new_len = _cmdqlen + self.size
        if cs.EUDIfNot()(c.Memory(_PROV_MAXBUFFER, c.AtMost, self.new_len + 1)):
            return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is None:
            _set_cmdqlen(self.new_len)
            cs.EUDEndIf()


@c.EUDFunc
def QueueGameCommand(data, size):  # noqa: N802
    """Queue game command to packet queue.

    Starcraft periodically broadcasts game packets to other player. Game
    packets are stored to queue, and this function add data to that queue, so
    that SC can broadcast it.

    :param data: Data to put in queue
    :param size: Size of data

    .. note::
        If packet queue is full, this function fails. This behavior is silent
        without any warning or error, since this behavior shouldn't happen in
        common situations. So **Don't use this function too much in a frame.**

    """
    with QueueGameCommandHelper(size) as qgc:
        f_memcpy(0x654880 + qgc.cmdqlen, data, qgc.size)


bw = EUDByteWriter()


@c.EUDFunc
def _qgc_alphaids(packet_id, n, arr_epd):
    """
    == 0x0B - Select Delta Del ==
    == 0x0A - Select Delta Add ==
    == 0x09 - Select Units ==
    """
    with QueueGameCommandHelper(2 + 2 * n) as qgc:
        bw.seekoffset(0x654880 + qgc.cmdqlen)
        bw.writebyte(packet_id)
        bw.writebyte(n)

        cp2arr = c.SetMemory(0x6509B0, c.SetTo, 0)
        cp2arr_quantity = EPD(cp2arr) + 5
        c.SetVariables(cp2arr_quantity, arr_epd)
        if cs.EUDWhileNot()(n.Exactly(0)):
            b0, b1 = c.EUDCreateVariables(2)
            restore_arr = c.SetDeaths(CurrentPlayer, c.Add, 0, 0)
            cp2uniqueness_identifier = c.SetMemory(0x6509B0, c.SetTo, 0)
            cp2ui_quantity = EPD(cp2uniqueness_identifier) + 5
            cunit_initval = EPD(0x59CCA8) + 0xA5 // 4
            c.RawTrigger(
                actions=[
                    cp2arr,
                    b0.SetNumber(1),
                    b1.SetNumber(0),
                    c.SetMemory(restore_arr + 20, c.SetTo, 0),
                    c.SetMemoryEPD(cp2ui_quantity, c.SetTo, cunit_initval),
                ]
            )
            for i in range(10, -1, -1):
                ptr = 0x59CCA8 + (336 << i)
                c.RawTrigger(
                    conditions=c.Deaths(CurrentPlayer, c.AtLeast, ptr, 0),
                    actions=[
                        c.SetDeaths(CurrentPlayer, c.Subtract, 336 << i, 0),
                        c.SetMemory(restore_arr + 20, c.Add, 336 << i),
                        c.SetMemoryEPD(cp2ui_quantity, c.Add, 84 << i),
                        b0.AddNumber(1 << i)
                        if i < 8
                        else b1.AddNumber(1 << (i - 8)),
                    ],
                )
            c.RawTrigger(
                conditions=b0.AtLeast(256),
                actions=[
                    b0.SubtractNumber(256),
                    b1.AddNumber(1),
                ],
            )
            c.RawTrigger(actions=[restore_arr, cp2uniqueness_identifier])
            for i in range(8):
                m = 1 << (i + 8)
                c.RawTrigger(
                    conditions=c.DeathsX(CurrentPlayer, c.AtLeast, 1, 0, m),
                    actions=b1.AddNumber(1 << (i + 3)),
                )
            bw.writebyte(b0)
            bw.writebyte(b1)
            c.SetVariables([cp2arr_quantity, n], [1, 1], [c.Add, c.Subtract])
        cs.EUDEndWhile()
        f_setcurpl2cpcache()


def QueueGameCommand_Select(n, ptr_arr):  # noqa: N802
    """
    == 0x09 - Select Units ==
    {{{
        BYTE bCount;
        WORD unitID[bCount];
    }}}
    """
    if isinstance(ptr_arr, int) or c.IsEUDVariable(ptr_arr):
        _qgc_alphaids(0x09, n, EPD(ptr_arr))
    elif c.IsConstExpr(ptr_arr) and ptr_arr._is_epd():
        _qgc_alphaids(0x09, n, ptr_arr)
    else:
        _qgc_alphaids(0x09, n, EPD(ptr_arr))


def QueueGameCommand_AddSelect(n, ptr_arr):  # noqa: N802
    """
    == 0x0A - Select Delta Add ==
    {{{
        BYTE bCount;
        WORD unitID[bCount];
    }}}
    """
    if isinstance(ptr_arr, int) or c.IsEUDVariable(ptr_arr):
        _qgc_alphaids(0x0A, n, EPD(ptr_arr))
    elif c.IsConstExpr(ptr_arr) and ptr_arr._is_epd():
        _qgc_alphaids(0x0A, n, ptr_arr)
    else:
        _qgc_alphaids(0x0A, n, EPD(ptr_arr))


def QueueGameCommand_RemoveSelect(n, ptr_arr):  # noqa: N802
    """
    == 0x0B - Select Delta Del ==
    {{{
        BYTE bCount;
        WORD unitID[bCount];
    }}}
    """
    if isinstance(ptr_arr, int) or c.IsEUDVariable(ptr_arr):
        _qgc_alphaids(0x0B, n, EPD(ptr_arr))
    elif c.IsConstExpr(ptr_arr) and ptr_arr._is_epd():
        _qgc_alphaids(0x0B, n, ptr_arr)
    else:
        _qgc_alphaids(0x0B, n, EPD(ptr_arr))


@c.EUDFunc
def QueueGameCommand_RightClick(xy):  # noqa: N802
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    right_click_command = c.Db(b"...\x14XXYY\0\0\xE4\0\x00")
    c.SetVariables(EPD(right_click_command + 4), xy)
    QueueGameCommand(right_click_command + 3, 10)


@c.EUDFunc
def QueueGameCommand_QueuedRightClick(xy):  # noqa: N802
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    queued_right_click_command = c.Db(b"...\x14XXYY\0\0\xE4\0\x01")
    c.SetVariables(EPD(queued_right_click_command + 4), xy)
    QueueGameCommand(queued_right_click_command + 3, 10)


@c.EUDFunc
def QueueGameCommand_MinimapPing(xy):  # noqa: N802
    """Queue minimap ping action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for minimap ping.
    """
    minimap_ping_command = c.Db(b"...\x58XXYY")
    c.SetVariables(EPD(minimap_ping_command + 4), xy)
    QueueGameCommand(minimap_ping_command + 3, 5)


@c.EUDTypedFunc([TrgUnit])
def QueueGameCommand_TrainUnit(unit):  # noqa: N802
    train_unit_command = c.Db(b"...\x1FUU..")
    c.SetVariables(EPD(train_unit_command + 4), unit)
    QueueGameCommand(train_unit_command + 3, 3)


@c.EUDFunc
def QueueGameCommand_PauseGame():  # noqa: N802
    pause_game_command = c.Db(b"\x10")
    QueueGameCommand(pause_game_command, 1)


@c.EUDFunc
def QueueGameCommand_ResumeGame():  # noqa: N802
    resume_game_command = c.Db(b"\x11")
    QueueGameCommand(resume_game_command, 1)


@c.EUDFunc
def QueueGameCommand_RestartGame():  # noqa: N802
    restart_game_command = c.Db(b"\x08")
    QueueGameCommand(restart_game_command, 1)


@c.EUDFunc
def QueueGameCommand_MergeDarkArchon():  # noqa: N802
    merge_dark_archon_command = c.Db(b"\x5A")
    QueueGameCommand(merge_dark_archon_command, 1)


@c.EUDFunc
def QueueGameCommand_MergeArchon():  # noqa: N802
    merge_archon_command = c.Db(b"\x2A")
    QueueGameCommand(merge_archon_command, 1)


@c.EUDFunc
def QueueGameCommand_UseCheat(flags):  # noqa: N802
    use_cheat_command = c.Db(b"...\x12CCCC")
    c.SetVariables(EPD(use_cheat_command + 4), flags)
    QueueGameCommand(use_cheat_command + 3, 5)
