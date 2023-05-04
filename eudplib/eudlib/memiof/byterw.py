#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ...core.variable.evcommon import _ev
from ...localize import _
from ...utils import EPD, EPError, RandList
from . import dwepdio as dwm
from . import modcurpl as cp


class EUDByteReader:
    """Read byte by byte."""

    def __init__(self):
        self._suboffset = c.EUDLightVariable()
        self._read = c.Forward()

    # -------

    def seekepd(self, epdoffset):
        """Seek EUDByteReader to specific epd player address"""
        if c.IsEUDVariable(epdoffset):
            return c.VProc(
                epdoffset,
                [
                    epdoffset.QueueAssignTo(EPD(self._read) + 5),
                    self._suboffset.SetNumber(0),
                ],
            )
        else:
            return c.RawTrigger(
                actions=[
                    c.SetMemory(self._read + 20, c.SetTo, epdoffset),
                    self._suboffset.SetNumber(0),
                ]
            )

    @c.EUDMethod
    def seekoffset(self, offset):
        """Seek EUDByteReader to specific address"""
        # convert offset to epd offset & suboffset
        c.f_div(offset, 4, ret=[EPD(self._read) + 5, self._suboffset])
        c.RawTrigger(actions=c.SetMemory(self._read + 20, c.Add, -(0x58A364 // 4)))

    # -------

    @c.EUDMethod
    def readbyte(self):
        """Read byte from current address. ByteReader will advance by 1 bytes.

        :returns: Read byte
        """
        case = [c.Forward() for _ in range(5)]
        ret = _ev[4]

        cs.DoActions(self._read << c.SetMemory(0x6509B0, c.SetTo, 0), ret.SetNumber(0))

        for i in range(4):
            case[i] << c.NextTrigger()
            if i < 3:
                cs.EUDJumpIfNot(self._suboffset == i, case[i + 1])
            for j in RandList(range(8)):
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** (j + 8 * i)),
                    actions=ret.AddNumber(2**j),
                )
            if i < 3:
                c.RawTrigger(nextptr=case[-1], actions=self._suboffset.AddNumber(1))
            else:  # suboffset == 3
                cs.DoActions(c.SetMemory(self._read + 20, c.Add, 1), self._suboffset.SetNumber(0))

        case[-1] << c.NextTrigger()
        cp.f_setcurpl2cpcache()
        return ret


class EUDByteWriter:
    """Write byte by byte."""

    def __init__(self):
        self._suboffset = c.EUDLightVariable()
        self._write = c.Forward()
        self._const = [c.Forward() for _ in range(4)]
        self._return = c.Forward()

    # -------

    def seekepd(self, epdoffset):
        """Seek EUDByteWriter to specific epd player address"""
        if c.IsEUDVariable(epdoffset):
            c.VProc(
                epdoffset,
                [
                    epdoffset.QueueAssignTo(EPD(self._write + 344)),
                    self._suboffset.SetNumber(0),
                ],
            )
        else:
            c.RawTrigger(
                actions=[
                    c.SetMemory(self._write + 344, c.SetTo, epdoffset),
                    self._suboffset.SetNumber(0),
                ]
            )

    @c.EUDMethod
    def seekoffset(self, offset):
        """Seek EUDByteWriter to specific address"""
        # convert offset to epd offset & suboffset
        c.f_div(offset, 4, ret=[EPD(self._write + 344), self._suboffset])
        c.RawTrigger(actions=c.SetMemory(self._write + 344, c.Add, -(0x58A364 // 4)))

    # -------

    @c.EUDMethod
    def _writebyte(self, byte):
        cs.EUDSwitch(self._suboffset)
        if cs.EUDSwitchCase()(0):
            c.VProc(
                byte,
                [
                    byte.SetDest(EPD(self._write + 348)),
                    c.SetMemory(self._write + 328, c.SetTo, 0xFF),
                ],
            )
            cs.EUDBreak()
        for i in range(1, 4):
            if cs.EUDSwitchCase()(i):
                cs.DoActions(c.SetMemory(self._write + 328, c.SetTo, 0xFF << (8 * i)))
                for j in RandList(range(8)):
                    c.RawTrigger(
                        conditions=byte.AtLeastX(1, 2**j),
                        actions=c.SetMemory(self._write + 348, c.Add, 2 ** (j + i * 8)),
                    )
                cs.EUDBreak()

        cs.EUDEndSwitch()

        self._write << c.RawTrigger(
            actions=(
                c.SetDeathsX(0, c.SetTo, 0, 0, 0xFF00),
                self._suboffset.AddNumber(1),
                c.SetMemory(self._write + 348, c.SetTo, 0),
            )
        )
        c.RawTrigger(
            conditions=[self._suboffset >= 4],
            actions=[
                self._suboffset.SetNumber(0),
                c.SetMemory(self._write + 344, c.Add, 1),
            ],
        )
        self._return << c.NextTrigger()

    def writebyte(self, byte):
        """Write byte to current position.

        Write a byte to current position of EUDByteWriter.
        ByteWriter will advance by 1 byte.
        """
        if c.IsEUDVariable(byte):
            return self._writebyte(byte)
        if not self._const[0].IsSet():
            c.PushTriggerScope()
            for i in range(4):
                self._const[i] << c.RawTrigger(
                    conditions=self._suboffset.Exactly(i),
                    actions=[
                        c.SetMemory(self._write + 348, c.SetTo, 0),
                        c.SetMemory(self._write + 328, c.SetTo, 0xFF << (8 * i)),
                    ],
                )
            c.SetNextTrigger(self._write)
            c.PopTriggerScope()
        nextptr = c.Forward()
        c.RawTrigger(
            nextptr=self._const[0],
            actions=[c.SetMemory(self._const[i] + 348, c.SetTo, byte << (8 * i)) for i in range(4)]
            + [c.SetNextPtr(self._return, nextptr)],
        )
        nextptr << c.NextTrigger()

    def flushdword(self):
        pass


class EUDByteStream:
    """Write and read byte by byte."""

    def __init__(self):
        self._offset = c.EUDVariable()
        self._suboffset = c.EUDVariable()

    # -------

    def seekepd(self, epdoffset):
        """Seek EUDByteWriter to specific epd player address"""
        if c.IsEUDVariable(epdoffset):
            c.VProc(
                epdoffset,
                [epdoffset.QueueAssignTo(self._offset), self._suboffset.SetNumber(0)],
            )
        else:
            c.RawTrigger(
                actions=[
                    self._offset.SetNumber(epdoffset),
                    self._suboffset.SetNumber(0),
                ]
            )

    @c.EUDMethod
    def seekoffset(self, offset):
        """Seek EUDByteWriter to specific address"""
        # convert offset to epd offset & suboffset
        c.f_div(offset, 4, ret=[self._offset, self._suboffset])
        self._offset += -(0x58A364 // 4)

    def copyto(self, bytestream):
        if isinstance(bytestream, EUDByteStream):
            offset = bytestream._offset
        elif isinstance(bytestream, EUDByteReader):
            offset = EPD(bytestream._read) + 5
        elif isinstance(bytestream, EUDByteWriter):
            offset = EPD(bytestream._write) + 4
        else:
            raise EPError(_("copyto target should be EUDByteReader/Writer/Stream"))
        c.VProc(
            [self._offset, self._suboffset],
            [
                self._offset.SetDest(offset),
                self._suboffset.SetDest(bytestream._suboffset),
            ],
        )

    # -------

    @c.EUDMethod
    def readbyte(self):
        """Read byte from current address. ByteReader will advance by 1 bytes.

        :returns: Read byte
        """
        case = [c.Forward() for _ in range(5)]
        ret = _ev[4]

        c.VProc(self._offset, [self._offset.SetDest(EPD(0x6509B0)), ret.SetNumber(0)])

        for i in range(4):
            case[i] << c.NextTrigger()
            if i < 3:
                cs.EUDJumpIfNot(self._suboffset == i, case[i + 1])
            for j in RandList(range(8)):
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** (j + 8 * i)),
                    actions=ret.AddNumber(2**j),
                )
            if i < 3:
                c.RawTrigger(nextptr=case[-1], actions=self._suboffset.AddNumber(1))
            else:  # suboffset == 3
                cs.DoActions(self._offset.AddNumber(1), self._suboffset.SetNumber(0))

        case[-1] << c.NextTrigger()
        cp.f_setcurpl2cpcache()
        return ret

    @c.EUDMethod
    def writebyte(self, byte):
        """Write byte to current position.

        Write a byte to current position of EUDByteWriter.
        ByteWriter will advance by 1 byte.
        """
        write = c.Forward()

        c.VProc(
            self._offset,
            [
                self._offset.SetDest(EPD(write) + 4),
                c.SetMemory(write + 20, c.SetTo, 0),
            ],
        )

        cs.EUDSwitch(self._suboffset)
        if cs.EUDSwitchCase()(0):
            c.VProc(
                byte,
                [
                    byte.SetDest(EPD(write) + 5),
                    c.SetMemory(write, c.SetTo, 0xFF),
                ],
            )
            cs.EUDBreak()
        for i in range(1, 4):
            if cs.EUDSwitchCase()(i):
                cs.DoActions(c.SetMemory(write, c.SetTo, 0xFF << (8 * i)))
                for j in RandList(range(8)):
                    c.RawTrigger(
                        conditions=byte.AtLeastX(1, 2**j),
                        actions=c.SetMemory(write + 20, c.Add, 2 ** (j + i * 8)),
                    )
                cs.EUDBreak()

        cs.EUDEndSwitch()

        cs.DoActions(
            self._suboffset.AddNumber(1),
            write << c.SetDeathsX(0, c.SetTo, 0, 0, 0),
        )
        c.RawTrigger(
            conditions=[self._suboffset >= 4],
            actions=[self._offset.AddNumber(1), self._suboffset.SetNumber(0)],
        )

    def flushdword(self):
        pass
