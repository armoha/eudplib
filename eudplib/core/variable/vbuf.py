#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections import deque
from typing import TYPE_CHECKING, Literal

from ... import utils as ut
from .. import rawtrigger as bt
from ..allocator import RegisterCreatePayloadCallback
from ..eudobj import EUDObject

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from .eudv import VariableTriggerForward


class EUDVarBuffer(EUDObject):
    """Variable buffer

    72 bytes per variable.
    """

    def __init__(self) -> None:
        super().__init__()

        self._vdict: "dict[VariableTriggerForward, int]" = {}
        self._initvals: "list[int | ConstExpr]" = []

    def DynamicConstructed(self) -> Literal[True]:
        return True

    def CreateVarTrigger(self, v, initval):
        ret = self + (72 * len(self._initvals))
        self._initvals.append(initval)
        self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + (72 * len(self._initvals))
        self._initvals.extend(initvals)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self) -> int:
        return 2408 + 72 * (len(self._initvals) - 1)

    def CollectDependency(self, emitbuffer) -> None:
        for initval in self._initvals:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer) -> None:
        emitbuffer.WriteSpace(4)

        for i in range(5):
            emitbuffer.WriteDword(0)  # nextptr
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(52 if i < 4 else 16)

        for i, initval in enumerate(self._initvals):
            emitbuffer.WriteDword(0xFFFFFFFF)  # bitmask
            emitbuffer.WriteSpace(12)
            emitbuffer.WriteDword(0)  # player
            emitbuffer.WriteDword(initval)
            emitbuffer.WriteDword(0x072D0000)  # unit, acttype, SetTo
            emitbuffer.WriteDword(0x43530000)  # actflag, SC
            emitbuffer.WriteByte(4)  # flags
            if i == len(self._initvals) - 1:
                break
            emitbuffer.WriteSpace(3)
            emitbuffer.WriteDword(0)  # nextptr
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(2)
            emitbuffer.WriteByte(0)  # noact
            emitbuffer.WriteSpace(13)

        emitbuffer.WriteSpace(25)
        emitbuffer.WriteByte(0)  # noact
        emitbuffer.WriteSpace(45)
        emitbuffer.WriteByte(4)  # flags

        for _ in range(27):
            emitbuffer.WriteSpace(71)
            emitbuffer.WriteByte(4)  # flags

        emitbuffer.WriteSpace(31)


_evb = None


def RegisterNewVariableBuffer() -> None:
    global _evb
    _evb = EUDVarBuffer()


def GetCurrentVariableBuffer():
    return _evb


RegisterCreatePayloadCallback(RegisterNewVariableBuffer)


class EUDCustomVarBuffer(EUDObject):
    """Customizable Variable buffer

    72 bytes per variable.
    """

    def __init__(self):
        super().__init__()

        self._vdict = {}
        self._5nptrs = deque([], maxlen=5)
        self._actnptr_pairs = []
        self._5acts = deque([], maxlen=5)

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, initval):
        # bitmask, player, #, modifier, nptr
        ret = self + 72 * (len(self._actnptr_pairs) + len(self._5acts))
        if len(self._5acts) == 5:
            act = self._5acts.popleft()
            act.append(initval[4])
            self._actnptr_pairs.append(act)
        else:
            self._5nptrs.append(initval[4])
        self._5acts.append(deque(initval[0:4], maxlen=5))
        if v is not None:
            self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + 72 * (len(self._actnptr_pairs) + len(self._5acts))
        for initval in initvals:
            self.CreateVarTrigger(None, initval)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2408 + 72 * (len(self._actnptr_pairs) + len(self._5acts) - 1)

    def CollectDependency(self, emitbuffer):
        for initval in self._5nptrs:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)
        for initvals in self._actnptr_pairs:
            for initval in initvals:
                if type(initval) is not int:
                    emitbuffer.WriteDword(initval)
        for initvals in self._5acts:
            for initval in initvals:
                if type(initval) is not int:
                    emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteSpace(4)

        for i in range(5):
            try:
                emitbuffer.WriteDword(self._5nptrs[i])  # nextptr
            except IndexError:
                emitbuffer.WriteSpace(19)
            else:
                emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(52 if i < 4 else 16)

        from itertools import chain

        # bitmask, player, initval, modifier, nptr
        for i, initvals in enumerate(chain(self._actnptr_pairs, self._5acts)):
            emitbuffer.WriteDword(initvals[0])  # bitmask
            emitbuffer.WriteSpace(12)
            emitbuffer.WriteDword(initvals[1])  # player
            emitbuffer.WriteDword(initvals[2])  # initval
            emitbuffer.WriteDword(initvals[3])  # unit, acttype, modifier
            emitbuffer.WriteDword(0x43530000)  # actflag, SC
            emitbuffer.WriteByte(4)  # flags
            if i == len(self._actnptr_pairs) + len(self._5acts) - 1:
                break
            if len(initvals) <= 4:
                emitbuffer.WriteSpace(22)
            else:
                emitbuffer.WriteSpace(3)
                emitbuffer.WriteDword(initvals[4])  # nextptr
                emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(2)
            emitbuffer.WriteByte(0)  # noact
            emitbuffer.WriteSpace(13)

        emitbuffer.WriteSpace(25)
        emitbuffer.WriteByte(0)  # noact
        emitbuffer.WriteSpace(45)
        emitbuffer.WriteByte(4)  # flags

        for _ in range(27):
            emitbuffer.WriteSpace(71)
            emitbuffer.WriteByte(4)  # flags

        emitbuffer.WriteSpace(31)


_ecvb = None


def RegisterNewCustomVariableBuffer():
    global _ecvb
    _ecvb = EUDCustomVarBuffer()


def GetCurrentCustomVariableBuffer():
    return _ecvb


RegisterCreatePayloadCallback(RegisterNewCustomVariableBuffer)
