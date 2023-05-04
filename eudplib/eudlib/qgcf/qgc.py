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
def QueueGameCommand(data, size):
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
def QueueGameCommand_Select(n, ptrList):
    ptrList = EUDArray.cast(ptrList)
    buf = c.Db(b"\x090123456789012345678901234")
    bw.seekoffset(buf + 1)
    bw.writebyte(n)
    i = c.EUDVariable()
    i << 0
    if cs.EUDWhile()(i < n):
        unitptr = ptrList[i]
        unitIndex = (unitptr - 0x59CCA8) // 336 + 1
        uniquenessIdentifier = f_bread(unitptr + 0xA5)
        targetID = unitIndex | c.f_bitlshift(uniquenessIdentifier, 11)
        b0, b1 = f_dwbreak(targetID)[2:4]
        bw.writebyte(b0)
        bw.writebyte(b1)
        i += 1
    cs.EUDEndWhile()
    QueueGameCommand(buf, 2 * (n + 1))


@c.EUDFunc
def QueueGameCommand_RightClick(xy):
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    RightClickCommand = c.Db(b"...\x14XXYY\0\0\xE4\0\x00")
    c.SetVariables(ut.EPD(RightClickCommand + 4), xy)
    QueueGameCommand(RightClickCommand + 3, 10)


@c.EUDFunc
def QueueGameCommand_QueuedRightClick(xy):
    """Queue right click action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for right click.
    """
    QueuedRightClickCommand = c.Db(b"...\x14XXYY\0\0\xE4\0\x01")
    c.SetVariables(ut.EPD(QueuedRightClickCommand + 4), xy)
    QueueGameCommand(QueuedRightClickCommand + 3, 10)


@c.EUDFunc
def QueueGameCommand_MinimapPing(xy):
    """Queue minimap ping action.

    :param xy: (y * 65536) + x, where (x, y) is coordinate for minimap ping.
    """
    MinimapPingCommand = c.Db(b"...\x58XXYY")
    c.SetVariables(ut.EPD(MinimapPingCommand + 4), xy)
    QueueGameCommand(MinimapPingCommand + 3, 5)


@c.EUDTypedFunc([c.TrgUnit])
def QueueGameCommand_TrainUnit(unit):
    TrainUnitCommand = c.Db(b"...\x1FUU..")
    c.SetVariables(ut.EPD(TrainUnitCommand + 4), unit)
    QueueGameCommand(TrainUnitCommand + 3, 3)


@c.EUDFunc
def QueueGameCommand_PauseGame():
    PauseGameCommand = c.Db(b"\x10")
    QueueGameCommand(PauseGameCommand, 1)


@c.EUDFunc
def QueueGameCommand_ResumeGame():
    ResumeGameCommand = c.Db(b"\x11")
    QueueGameCommand(ResumeGameCommand, 1)


@c.EUDFunc
def QueueGameCommand_RestartGame():
    RestartGameCommand = c.Db(b"\x08")
    QueueGameCommand(RestartGameCommand, 1)


@c.EUDFunc
def QueueGameCommand_MergeDarkArchon():
    MergeDarkArchonCommand = c.Db(b"\x5A")
    QueueGameCommand(MergeDarkArchonCommand, 1)


@c.EUDFunc
def QueueGameCommand_MergeArchon():
    MergeArchonCommand = c.Db(b"\x2A")
    QueueGameCommand(MergeArchonCommand, 1)


@c.EUDFunc
def QueueGameCommand_UseCheat(flags):
    UseCheatCommand = c.Db(b"...\x12CCCC")
    c.SetVariables(ut.EPD(UseCheatCommand + 4), flags)
    QueueGameCommand(UseCheatCommand + 3, 5)
