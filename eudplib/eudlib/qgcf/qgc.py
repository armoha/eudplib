#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..eudarray import EUDArray
from ..memiof import EUDByteWriter, f_bread, f_dwbreak, f_dwread_epd, f_memcpy


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
    prov_maxbuffer = f_dwread_epd(ut.EPD(0x57F0D8))
    cmdqlen = f_dwread_epd(ut.EPD(0x654AA0))
    if cs.EUDIfNot()(cmdqlen + size + 1 >= prov_maxbuffer):
        f_memcpy(0x654880 + cmdqlen, data, size)
        c.SetVariables(ut.EPD(0x654AA0), cmdqlen + size)
    cs.EUDEndIf()


bw = EUDByteWriter()


@c.EUDFunc
def QueueGameCommand_Select(n, ptr_arr):  # noqa: N802
    ptr_arr = EUDArray.cast(ptr_arr)
    buf = c.Db(b"\x090123456789012345678901234")
    bw.seekoffset(buf + 1)
    bw.writebyte(n)
    i = c.EUDVariable()
    i << 0
    if cs.EUDWhile()(i < n):
        unitptr = ptr_arr[i]
        unit_index = (unitptr - 0x59CCA8) // 336 + 1
        uniqueness_identifier = f_bread(unitptr + 0xA5)
        target_id = unit_index | c.f_bitlshift(uniqueness_identifier, 11)
        b0, b1 = f_dwbreak(target_id)[2:4]
        bw.writebyte(b0)
        bw.writebyte(b1)
        i += 1
    cs.EUDEndWhile()
    QueueGameCommand(buf, 2 * (n + 1))


@c.EUDFunc
def QueueGameCommand_RightClick(xy):  # noqa: N802
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    right_click_command = c.Db(b"...\x14XXYY\0\0\xE4\0\x00")
    c.SetVariables(ut.EPD(right_click_command + 4), xy)
    QueueGameCommand(right_click_command + 3, 10)


@c.EUDFunc
def QueueGameCommand_QueuedRightClick(xy):  # noqa: N802
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    queued_right_click_command = c.Db(b"...\x14XXYY\0\0\xE4\0\x01")
    c.SetVariables(ut.EPD(queued_right_click_command + 4), xy)
    QueueGameCommand(queued_right_click_command + 3, 10)


@c.EUDFunc
def QueueGameCommand_MinimapPing(xy):  # noqa: N802
    """Queue minimap ping action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for minimap ping.
    """
    minimap_ping_command = c.Db(b"...\x58XXYY")
    c.SetVariables(ut.EPD(minimap_ping_command + 4), xy)
    QueueGameCommand(minimap_ping_command + 3, 5)


@c.EUDTypedFunc([c.TrgUnit])
def QueueGameCommand_TrainUnit(unit):  # noqa: N802
    train_unit_command = c.Db(b"...\x1FUU..")
    c.SetVariables(ut.EPD(train_unit_command + 4), unit)
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
    c.SetVariables(ut.EPD(use_cheat_command + 4), flags)
    QueueGameCommand(use_cheat_command + 3, 5)
