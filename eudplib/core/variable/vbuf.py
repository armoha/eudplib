#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections import deque
from typing import TYPE_CHECKING, Literal

from ... import utils as ut
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

    def DynamicConstructed(self) -> Literal[True]:  # noqa: N802
        return True

    def create_vartrigger(self, v, initval):
        ret = self + (72 * len(self._initvals))
        self._initvals.append(initval)
        self._vdict[v] = ret
        return ret

    def create_vartriggers(self, v, initvals):
        ret = self + (72 * len(self._initvals))
        self._initvals.extend(initvals)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self) -> int:  # noqa: N802
        return 2408 + 72 * (len(self._initvals) - 1)

    def CollectDependency(self, emitbuffer) -> None:  # noqa: N802
        for initval in self._initvals:
            if not isinstance(initval, int):
                emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer) -> None:  # noqa: N802
        emitbuffer.WriteSpace(4)

        for _ in range(4):
            emitbuffer.WriteDword(0)  # nextptr
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            emitbuffer.WriteSpace(52)

        emitbuffer.WriteDword(0)  # nextptr
        emitbuffer.WriteSpace(15)
        emitbuffer.WriteByte(0)  # nocond
        emitbuffer.WriteSpace(16)

        output = bytearray(72 * len(self._initvals))

        for i in range(len(self._initvals)):
            # 'preserve rawtrigger'
            output[72 * i : 72 * i + 4] = b"\xFF\xFF\xFF\xFF"
            output[72 * i + 24 : 72 * i + 28] = b"\0\0\x2D\x07"
            output[72 * i + 28 : 72 * i + 32] = b"\0\0SC"
            output[72 * i + 32 : 72 * i + 36] = b"\x04\0\0\0"

        heads = 0
        for i, initval in enumerate(self._initvals):
            heade = 72 * i + 20
            if initval == 0:
                continue
            elif isinstance(initval, int):
                output[heade : heade + 4] = ut.i2b4(initval)
                continue
            emitbuffer.WriteBytes(output[heads:heade])
            emitbuffer.WriteDword(initval)
            heads = 72 * i + 24

        emitbuffer.WriteBytes(output[heads:])

        emitbuffer.WriteSpace(32)
        emitbuffer.WriteDword(4)  # flags
        emitbuffer.WriteSpace(27)
        emitbuffer.WriteByte(0)  # currentAction

        for _ in range(27):
            emitbuffer.WriteSpace(40)
            emitbuffer.WriteDword(4)  # flags
            emitbuffer.WriteSpace(27)
            emitbuffer.WriteByte(0)  # currentAction


_evb = None


def _register_new_varbuffer() -> None:
    global _evb
    _evb = EUDVarBuffer()


def get_current_varbuffer():
    return _evb


RegisterCreatePayloadCallback(_register_new_varbuffer)


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

    def DynamicConstructed(self):  # noqa: N802
        return True

    def create_vartrigger(self, v, initval):
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

    def create_vartriggers(self, v, initvals):
        ret = self + 72 * (len(self._actnptr_pairs) + len(self._5acts))
        for initval in initvals:
            self.create_vartrigger(None, initval)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):  # noqa: N802
        return 2408 + 72 * (len(self._actnptr_pairs) + len(self._5acts) - 1)

    def CollectDependency(self, emitbuffer):  # noqa: N802
        for initval in self._5nptrs:
            if not isinstance(initval, int):
                emitbuffer.WriteDword(initval)
        for initvals in self._actnptr_pairs:
            for initval in initvals:
                if not isinstance(initval, int):
                    emitbuffer.WriteDword(initval)
        for initvals in self._5acts:
            for initval in initvals:
                if not isinstance(initval, int):
                    emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):  # noqa: N802
        output = bytearray(72 * (len(self._actnptr_pairs) + len(self._5acts)))

        emitbuffer.WriteSpace(4)

        for i in range(5):
            try:
                emitbuffer.WriteDword(self._5nptrs[i])  # nextptr
            except IndexError:
                emitbuffer.WriteDword(0)
            emitbuffer.WriteSpace(15)
            emitbuffer.WriteByte(0)  # nocond
            if i < 4:
                emitbuffer.WriteSpace(52)
            else:
                emitbuffer.WriteSpace(16)

        for i in range(len(self._actnptr_pairs) + len(self._5acts)):
            # 'preserve rawtrigger'
            output[72 * i : 72 * i + 4] = b"\xFF\xFF\xFF\xFF"
            output[72 * i + 24 : 72 * i + 28] = b"\0\0\x2D\x07"
            output[72 * i + 28 : 72 * i + 32] = b"\0\0SC"
            output[72 * i + 32 : 72 * i + 36] = b"\x04\0\0\0"

        heads = 0

        from itertools import chain

        # bitmask, player, initval, modifier, nptr
        offsets = (0, 16, 20, 24, 36)
        initials = (0xFFFFFFFF, 0, 0, 0x072D0000, 0)
        for i, initvals in enumerate(chain(self._actnptr_pairs, self._5acts)):
            for initval, offset, initial in zip(initvals, offsets, initials):
                heade = 72 * i + offset
                if initval == initial:
                    continue
                elif isinstance(initval, int):
                    output[heade : heade + 4] = ut.i2b4(initval)
                    continue
                emitbuffer.WriteBytes(output[heads:heade])
                emitbuffer.WriteDword(initval)
                heads = 72 * i + offset + 4

        emitbuffer.WriteBytes(output[heads:])

        emitbuffer.WriteSpace(32)
        emitbuffer.WriteDword(4)  # flags
        emitbuffer.WriteSpace(27)
        emitbuffer.WriteByte(0)  # currentAction

        for _ in range(27):
            emitbuffer.WriteSpace(40)
            emitbuffer.WriteDword(4)  # flags
            emitbuffer.WriteSpace(27)
            emitbuffer.WriteByte(0)  # currentAction


_ecvb = None


def _register_new_custom_varbuffer():
    global _ecvb
    _ecvb = EUDCustomVarBuffer()


def get_current_custom_varbuffer():
    return _ecvb


RegisterCreatePayloadCallback(_register_new_custom_varbuffer)
